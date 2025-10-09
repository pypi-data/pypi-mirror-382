# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

"""Expression evaluation for the feature-check Python library."""

from __future__ import annotations

import dataclasses
from collections.abc import Callable
from typing import Final

from . import defs
from . import version as fver


BoolOpFunction = Callable[[list[defs.Result]], bool]


@dataclasses.dataclass(frozen=True)
class ResultBool(defs.Result):
    """A boolean result of an expression; the "value" member is boolean."""

    value: bool

    def __str__(self) -> str:
        """Provide a human-readable representation of the calculation result."""
        return f"ResultBool: {self.value}"


@dataclasses.dataclass(frozen=True)
class ResultVersion(defs.Result):
    """A version number as a result of an expression.

    The "value" member is the version number string.
    """

    value: fver.Version

    def __str__(self) -> str:
        """Provide a human-readable representation of the calculation result."""
        return f"ResultVersion: {self.value.value}"


@dataclasses.dataclass(frozen=True)
class ExprFeature(defs.Expr):
    """An expression that returns a program feature name as a string."""

    name: str

    def evaluate(self, data: dict[str, fver.Version]) -> ResultVersion:
        """Look up the feature, return the result in a ResultVersion object."""
        return ResultVersion(value=data[self.name])


@dataclasses.dataclass(frozen=True)
class ExprVersion(defs.Expr):
    """An expression that returns a version number for a feature."""

    value: fver.Version

    def evaluate(self, _data: dict[str, fver.Version]) -> ResultVersion:
        """Return the version number as a ResultVersion object."""
        return ResultVersion(value=self.value)


@dataclasses.dataclass(frozen=True)
class BoolOp:
    """A two-argument boolean operation."""

    args: list[type[defs.Result]]
    action: BoolOpFunction


def _def_op_bool_ver(check: Callable[[int], bool]) -> BoolOpFunction:
    def _op_bool_ver(args: list[defs.Result]) -> bool:
        """Check whether the arguments are in the expected relation."""
        match args:
            case [left, right] if isinstance(left, ResultVersion) and isinstance(
                right,
                ResultVersion,
            ):
                return check(fver.version_compare(left.value, right.value))

        raise TypeError(args)

    return _op_bool_ver


NAMED_OPS = {
    "lt": BoolOp(
        args=[ResultVersion, ResultVersion],
        action=_def_op_bool_ver(lambda res: res < 0),
    ),
    "le": BoolOp(
        args=[ResultVersion, ResultVersion],
        action=_def_op_bool_ver(lambda res: res <= 0),
    ),
    "eq": BoolOp(
        args=[ResultVersion, ResultVersion],
        action=_def_op_bool_ver(lambda res: res == 0),
    ),
    "ge": BoolOp(
        args=[ResultVersion, ResultVersion],
        action=_def_op_bool_ver(lambda res: res >= 0),
    ),
    "gt": BoolOp(
        args=[ResultVersion, ResultVersion],
        action=_def_op_bool_ver(lambda res: res > 0),
    ),
}

SYNONYMS = {"<": "lt", "<=": "le", "=": "eq", ">=": "ge", ">": "gt"}

OPS = dict(
    list(NAMED_OPS.items()) + [(name, NAMED_OPS[value]) for name, value in SYNONYMS.items()],
)


@dataclasses.dataclass(frozen=True)
class ExprOp(defs.Expr):
    """A two-argument operation expression."""

    op: BoolOp
    args: list[defs.Expr]

    def __post_init__(self) -> None:
        """Validate the passed arguments."""
        if len(self.args) != len(self.op.args):
            raise ValueError((self.args, self.op.args))

    def evaluate(self, data: dict[str, fver.Version]) -> ResultBool:
        """Evaluate the expression over the specified data."""
        args: Final = [expr.evaluate(data) for expr in self.args]

        for idx, value in enumerate(args):
            if not isinstance(value, self.op.args[idx]):
                raise TypeError((idx, self.op.args[idx], value))

        return ResultBool(value=self.op.action(args))
