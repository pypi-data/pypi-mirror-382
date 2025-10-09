#!/bin/sh
#
# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

: "${PYTHON3:=python3}"

env PYTHONPATH="$(dirname -- "$(dirname -- "$0")")/src${PYTHONPATH+:${PYTHONPATH}}" \
    "$PYTHON3" -m feature_check "$@"
