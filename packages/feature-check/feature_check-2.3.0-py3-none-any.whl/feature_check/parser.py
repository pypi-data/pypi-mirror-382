# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

"""Parse feature names, versions, and simple expressions."""

from __future__ import annotations

from typing import Final

import pyparsing as pyp

from . import defs
from . import expr as fexpr
from . import version as fver


_p_comp_num: Final = pyp.Word(pyp.srange("[0-9]"))

_p_comp_rest: Final = pyp.Word(pyp.srange("[A-Za-z~-]"), pyp.srange("[0-9A-Za-z~-]"))

_p_version_comp: Final = (
    _p_comp_num.set_results_name("num") + pyp.Opt(_p_comp_rest.set_results_name("rest_first"))
) | _p_comp_rest.set_results_name("rest_only")

_p_version: Final = _p_version_comp + pyp.ZeroOrMore(pyp.Char(".").suppress() + _p_version_comp)

_p_feature: Final = pyp.Word(pyp.srange("[A-Za-z0-9_-]"))

_p_op_sign: Final = pyp.one_of(["<=", "<", "=", ">=", ">"])

_p_op_word: Final = pyp.one_of(["le", "lt", "eq", "ge", "gt"])

_p_op_sign_and_value: Final = (
    pyp.Opt(pyp.White()).suppress() + _p_op_sign + pyp.Opt(pyp.White()).suppress() + _p_version
)

_p_op_word_and_value: Final = (
    pyp.White().suppress() + _p_op_word + pyp.White().suppress() + _p_version
)

_p_expr: Final = _p_feature + pyp.Opt(_p_op_sign_and_value | _p_op_word_and_value)

_p_feature_version: Final = _p_feature + pyp.Opt(pyp.Literal("=").suppress() + _p_version)

_p_features_line: Final = _p_feature_version + pyp.ZeroOrMore(
    pyp.White().suppress() + _p_feature_version,
)


@_p_version_comp.set_parse_action
def _process_version_comp(tokens: pyp.ParseResults) -> fver.VersionComponent:
    """Build a `VersionComponent` object out of the numeric and string parts."""
    tok_dict: Final[dict[str, str]] = tokens.as_dict()
    num_str: Final = tok_dict.get("num")
    rest: Final = tok_dict.get("rest_first", tok_dict.get("rest_only", ""))
    return fver.VersionComponent(num=int(num_str) if num_str is not None else None, rest=rest)


@_p_version.set_parse_action
def _process_version(tokens: pyp.ParseResults) -> fver.Version:
    """Build a `Version` object out of the version components."""
    res: Final = tokens.as_list()
    if not all(isinstance(comp, fver.VersionComponent) for comp in res):
        raise ParseError(2, f"Weird version parse result: {res!r}")

    return fver.Version(value=".".join(str(comp) for comp in res), components=res)


@_p_op_sign.set_parse_action
def _parse_op_sign(tokens: pyp.ParseResults) -> fexpr.BoolOp:
    """Parse a boolean operation written as a sign ("<", ">=", etc)."""
    return fexpr.OPS[tokens[0]]


@_p_op_word.set_parse_action
def _parse_op_word(tokens: pyp.ParseResults) -> fexpr.BoolOp:
    """Parse a boolean operation written as a sign ("lt", "ge", etc)."""
    return fexpr.OPS[tokens[0]]


@_p_expr.set_parse_action
def _parse_expr(tokens: pyp.ParseResults) -> defs.Mode:
    """Build a `Mode` out of a single feature name or a simple expression."""
    res: Final = tokens.as_list()
    match res:
        case [feature_name] if isinstance(feature_name, str):
            return defs.ModeSingle(feature=feature_name, ast=fexpr.ExprFeature(feature_name))

        case [feature_name, cmp_op, ver] if (
            isinstance(feature_name, str)
            and isinstance(
                cmp_op,
                fexpr.BoolOp,
            )
            and isinstance(ver, fver.Version)
        ):
            return defs.ModeSimple(
                ast=fexpr.ExprOp(
                    op=cmp_op,
                    args=[fexpr.ExprFeature(feature_name), fexpr.ExprVersion(ver)],
                ),
            )

    raise ParseError(2, f"Weird expr parse results: {res!r}")


@_p_feature_version.set_parse_action
def _parse_feature_version(tokens: pyp.ParseResults) -> tuple[str, fver.Version]:
    """Parse a feature name and a version, defaulting to "1.0"."""
    res: Final = tokens.as_list()
    match res:
        case [feature] if isinstance(feature, str):
            return (feature, parse_version("1.0"))

        case [feature, ver] if isinstance(feature, str) and isinstance(ver, fver.Version):
            return (feature, ver)

    raise ParseError(2, f"Weird feature/version parse results: {res!r}")


@_p_features_line.set_parse_action
def _parse_features_line(tokens: pyp.ParseResults) -> dict[str, fver.Version]:
    """Build a features dictionary out of the parsed name/version tuples."""

    # We lie a little bit, or mypy won't be happy.
    def validate_pair(pair: tuple[str, fver.Version]) -> tuple[str, fver.Version]:
        """Validate a single parsed result."""
        match pair:
            case (name, value) if isinstance(name, str) and isinstance(value, fver.Version):
                return name, value

        raise ParseError(2, f"Weird features line parse result: {pair!r}")

    res: Final = tokens.as_list()
    return dict(validate_pair(pair) for pair in res)


_p_version_complete: Final = _p_version.leave_whitespace()

_p_expr_complete: Final = _p_expr.leave_whitespace()

_p_features_line_complete: Final = _p_features_line.leave_whitespace()


class ParseError(defs.FCError):
    """An error that occurred while parsing the expression."""


def parse_version(value: str) -> fver.Version:
    """Parse a version string into a `Version` object."""
    res: Final = _p_version_complete.parse_string(value).as_list()
    match res:
        case [ver] if isinstance(ver, fver.Version) and ver.value == value:
            return ver

        case [ver]:
            raise ParseError(
                2,
                f"Could not parse the whole of {value!r} as a version string "
                f"(parsed {ver!r} from {res!r})",
            )

    raise ParseError(2, f"Could not parse {value!r} as a version string (result: {res!r})")


def parse_expr(expr: str) -> defs.Mode:
    """Parse a simple "feature-name op version" expression.

    If the expression is valid, return an `Expr` object corresponding
    to the specified check.  Use this object's `evaluate()` method and
    pass a features dictionary as returned by the `obtain_features()`
    function to get a `Result` object; for simple expressions it will be
    a `ResultBool` object with a boolean `value` member.

        from feature_check import expr as fexpr
        from feature_check import obtain as fobtain

        data = fobtain.obtain_features("timelimit");
        expr = fexpr.parse_simple("subsecond > 0")
        print(expr.evaluate(data).value)
    """
    res: Final = _p_expr_complete.parse_string(expr).as_list()
    match res:
        case [mode] if isinstance(mode, defs.Mode):
            return mode

    raise ParseError(2, f"Could not parse {expr!r} as an expression (results: {res!r})")


def parse_features_line(features_line: str) -> dict[str, fver.Version]:
    """Parse the features list, default to version "1.0"."""
    try:
        res: Final = _p_features_line_complete.parse_string(features_line).as_list()
    except pyp.exceptions.ParseBaseException as err:
        raise ParseError(2, f"Could not parse {features_line!r} as a features line: {err}") from err
    match res:
        case [features] if isinstance(features, dict):
            return features

    raise ParseError(
        2,
        f"Could not parse {features_line!r} as a features line (results: {res!r})",
    )
