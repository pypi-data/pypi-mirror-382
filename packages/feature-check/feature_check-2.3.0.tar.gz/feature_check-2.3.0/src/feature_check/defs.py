# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

"""Constant definitions for the feature-check Python library."""

from __future__ import annotations

import abc
import dataclasses
import typing


if typing.TYPE_CHECKING:
    from . import version as fver


DEFAULT_OPTION = "--features"
"""The default command-line option to pass to a program to query for supported features."""

DEFAULT_PREFIX = "Features: "
"""The default prefix of the program's features output line."""

DEFAULT_OUTPUT_FMT = "tsv"
"""The default output format for the `feature-check` command-line tool."""

VERSION = "2.3.0"
"""The feature-check library version, SemVer-style."""

VERSION_STRING = VERSION


class FCError(Exception):
    """A base class for errors in handling a feature-check request."""

    def __init__(self, code: int, msg: str) -> None:
        """Initialize an error object."""
        super().__init__(msg)
        self._code = code
        self._msg = msg

    @property
    def code(self) -> int:
        """Return the numeric error code."""
        return self._code

    @property
    def message(self) -> str:
        """Return a human-readable error message."""
        return self._msg


@dataclasses.dataclass(frozen=True)
class Result:
    """The base class for an expression result."""


@dataclasses.dataclass(frozen=True)
class Expr(abc.ABC):
    """The (pretty much abstract) base class for an expression."""

    @abc.abstractmethod
    def evaluate(self, data: dict[str, fver.Version]) -> Result:
        """Evaluate the expression and return a Result object.

        Overridden in actual expression classes.
        """
        raise NotImplementedError(
            f"{type(self).__name__}.evaluate() must be overridden",  # noqa: EM102
        )


@dataclasses.dataclass(frozen=True)
class Mode:
    """Base class for the feature-check operating modes."""


@dataclasses.dataclass(frozen=True)
class ModeList(Mode):
    """List the features supported by the program."""


@dataclasses.dataclass(frozen=True)
class ModeSingle(Mode):
    """Query for the presence or the version of a single feature."""

    feature: str
    ast: Expr


@dataclasses.dataclass(frozen=True)
class ModeSimple(Mode):
    """Verify whether a simple 'feature op version' expression holds true."""

    ast: Expr
