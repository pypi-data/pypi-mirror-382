# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

"""Test the version comparison functions."""

from __future__ import annotations

from typing import Final

import pytest

from feature_check import defs
from feature_check import expr as fexpr
from feature_check import parser as fparser
from feature_check import version as fver

from . import data


def parsed_features() -> dict[str, fver.Version]:
    """Parse the versions of the features used in the test."""
    return {name: fparser.parse_version(value) for name, value in data.FEATURES.items()}


def do_test_compare(var: str, op_name: str, right: str, *, expected: bool) -> None:
    """Test the comparison functions."""
    feature: Final = f"{var} {op_name} {right}"
    mode: Final = fparser.parse_expr(feature)
    assert isinstance(mode, defs.ModeSimple)
    expr: Final = mode.ast
    assert isinstance(expr, fexpr.ExprOp)
    assert len(expr.args) == 2  # noqa: PLR2004
    assert isinstance(expr.args[0], fexpr.ExprFeature)
    assert isinstance(expr.args[1], fexpr.ExprVersion)

    res: Final = expr.evaluate(parsed_features())
    assert isinstance(res, fexpr.ResultBool)
    assert res.value == expected


@pytest.mark.parametrize(("var", "op_name", "right", "expected"), data.COMPARE)
def test_compare(*, var: str, op_name: str, right: str, expected: bool) -> None:
    """Test the comparison functions with word operands."""
    return do_test_compare(var, op_name, right, expected=expected)


@pytest.mark.parametrize(("var", "op_name", "right", "expected"), data.COMPARE)
def test_synonyms(*, var: str, op_name: str, right: str, expected: bool) -> None:
    """Test the comparison functions with word operands."""
    return do_test_compare(var, data.SYNONYMS[op_name], right, expected=expected)


@pytest.mark.parametrize("var", (item[0] for item in data.COMPARE))
def test_single(*, var: str) -> None:
    """Test obtaining the version of a single feature."""
    mode: Final = fparser.parse_expr(var)
    assert isinstance(mode, defs.ModeSingle)
    assert mode.feature == var
    expr: Final = mode.ast
    assert isinstance(expr, fexpr.ExprFeature)
    assert expr.name == var

    res: Final = expr.evaluate(parsed_features())
    assert isinstance(res, fexpr.ResultVersion)
    ver: Final = res.value
    assert ver.value
    assert ver.components
