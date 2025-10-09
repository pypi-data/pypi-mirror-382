# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

"""Query a program for the list of features that it supports."""

from __future__ import annotations

import subprocess  # noqa: S404
from typing import Final

from . import defs
from . import parser as fparser
from . import version as fver


class ObtainError(defs.FCError):
    """A base class for errors in obtaining the program's features."""


class ObtainExecError(ObtainError):
    """An error that occurred while executing the queried program."""

    def __init__(self, err: str) -> None:
        """Initialize an error object."""
        super().__init__(1, err)


class ObtainNoFeaturesSupportError(ObtainExecError):
    """The program does not seem to support the "--features" option."""

    def __init__(self, program: str, option: str) -> None:
        """Store the program name."""
        super().__init__(
            f"The {program} program does not seem to support "
            f"the {option} option for querying features",
        )


class ObtainNoFeaturesError(ObtainError):
    """An error that occurred while looking for the features line."""

    def __init__(self, program: str, option: str, prefix: str) -> None:
        """Initialize an error object."""
        super().__init__(
            2,
            f"The '{program} {option}' output did not contain a single '{prefix}' line",
        )


def obtain_features(
    program: str,
    option: str = defs.DEFAULT_OPTION,
    prefix: str = defs.DEFAULT_PREFIX,
) -> dict[str, fver.Version]:
    """Execute the specified program and get its list of features.

    The program is run with the specified query option (default:
    "--features") and its output is examined for a line starting with
    the specified prefix (default: "Features: ").  The rest of the line
    is parsed as a whitespace-separated list of either feature names or
    "name=version" pairs.  The function returns a dictionary of the features
    obtained with their versions (or "1.0" if only a feature name was found
    in the program's output).

        import feature_check

        data = feature_check.obtain_features("timelimit")
        print(data.get("subsecond", "not supported"))

    For programs that need a different command-line option to list features:

        import feature_check

        print("SSL" in feature_check.obtain_features("curl",
                                                     option="--version"))
    """

    def try_run() -> list[str]:
        """Query a program about its features, return the output lines."""
        res: Final = subprocess.run(  # noqa: S603
            [program, option],
            capture_output=True,
            check=False,
            stdin=None,
        )
        if res.returncode != 0 or res.stderr.decode():
            # It does not support '--features', does it?
            raise ObtainNoFeaturesSupportError(program, option)

        return res.stdout.decode().split("\n")

    try:
        lines: Final = try_run()
    except ObtainExecError:
        raise
    # Yes, we do want to convert any error into an ObtainExecError one
    except Exception as exc:
        # Something went wrong in the --features processing
        raise ObtainExecError(str(exc)) from exc

    matching: Final = (
        [
            rest
            for line, rest in ((line, line.removeprefix(prefix)) for line in lines)
            if rest != line
        ]
        if prefix
        else [line for line in lines if line]
    )
    if len(matching) != 1:
        raise ObtainNoFeaturesError(program, option, prefix)

    return fparser.parse_features_line(matching[0])
