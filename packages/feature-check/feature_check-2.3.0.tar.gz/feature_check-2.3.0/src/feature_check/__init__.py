# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

"""Base module for the feature-check Python library.

This module imports the `obtain_features()`, `parse_expr()`, and
`parse_version()` functions from the `feature_check.obtain`,
`feature_check.expr`, and `feature_check.version` submodules;
see their documentation for details.
"""

# isort: skip_file

from .defs import VERSION
from .expr import ResultBool, ResultVersion
from .obtain import obtain_features
from .parser import parse_expr, parse_version
from .version import Version, VersionComponent

__all__ = [
    "VERSION",
    "ResultBool",
    "ResultVersion",
    "Version",
    "VersionComponent",
    "obtain_features",
    "parse_expr",
    "parse_version",
]
