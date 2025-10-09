# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""A set of Hypothesis-based correctness tests."""

from __future__ import annotations

import contextlib
import subprocess  # noqa: S404
import typing
from unittest import mock

import hypothesis as hyp
import hypothesis.strategies as strat

from feature_check import defs as fdefs
from feature_check import obtain as fobtain
from feature_check import parser as fparser


if typing.TYPE_CHECKING:
    from typing import Final


ALPHABET_NAME: Final = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_"
ALPHABET_VER_FIRST: Final = "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
ALPHABET_VER_REST: Final = f"0{ALPHABET_VER_FIRST}"

STRAT_COMPONENT: Final = strat.tuples(
    strat.text(ALPHABET_VER_FIRST, min_size=1, max_size=1),
    strat.text(ALPHABET_VER_REST),
)

STRAT_FEATURES: Final = strat.lists(
    strat.tuples(strat.text(ALPHABET_NAME, min_size=1), strat.lists(STRAT_COMPONENT, min_size=1)),
    min_size=1,
)


def build_features(pairs: list[tuple[str, list[tuple[str, str]]]]) -> list[tuple[str, str]]:
    """Build a list of (name, version) pairs out of the feature components."""
    return [(name, ".".join(f"{first}{rest}" for first, rest in comps)) for name, comps in pairs]


@hyp.given(line=strat.text())
@hyp.example("")
def test_parse_exception(line: str) -> None:
    """Make sure the parser returns either success or our own exception."""
    with contextlib.suppress(fdefs.FCError):
        fparser.parse_features_line(line)


@hyp.given(pairs=STRAT_FEATURES)
def test_parse_pairs(pairs: list[tuple[str, list[tuple[str, str]]]]) -> None:
    """Make sure the parser returns the expected dictionary of feature names and versions."""
    paired: Final = build_features(pairs)
    exp: Final = dict(paired)
    line: Final = " ".join(f"{name}={ver}" for name, ver in paired)
    features: Final = fparser.parse_features_line(line)
    res: Final = {name: ver.value for name, ver in features.items()}
    assert res == exp


@hyp.given(
    program=strat.text(min_size=1),
    option=strat.text(min_size=1),
    prefix=strat.text(ALPHABET_NAME),
    pairs=STRAT_FEATURES,
)
@hyp.example("0", "0", "", [("A", [("1", "")])])
def test_parse_features_line(
    program: str,
    option: str,
    prefix: str,
    pairs: list[tuple[str, list[tuple[str, str]]]],
) -> None:
    """Make sure a full line can be parsed."""
    paired: Final = build_features(pairs)
    exp: Final = dict(paired)
    line: Final = prefix + " ".join(f"{name}={ver}" for name, ver in paired)

    def mock_subprocess_run(
        args: list[str],
        *,
        capture_output: bool = False,
        check: bool = True,
        stdin: str | None = "oof?",
    ) -> subprocess.CompletedProcess[bytes]:
        """Mock the invocation of an external program."""
        assert args == [program, option]
        assert capture_output
        assert not check
        assert stdin is None
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout=f"{line}\n".encode(),
            stderr=b"",
        )

    with mock.patch("subprocess.run", new=mock_subprocess_run):
        features: Final = fobtain.obtain_features(program, option, prefix)

    res: Final = {name: ver.value for name, ver in features.items()}
    assert res == exp
