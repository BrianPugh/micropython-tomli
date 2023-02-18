# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021 Taneli Hukkinen
# Licensed to PSF under a Contributor Agreement.

import re

RE_NUMBER = re.compile(
    r"""0(x[0-9A-Fa-f](_?[0-9A-Fa-f])*|b[01](_?[01])*|o[0-7](_?[0-7])*)|[+-]?(0|[1-9](_?[0-9])*)((\.[0-9](_?[0-9])*)?([eE][+-]?[0-9](_?[0-9])*)?)"""
)

def match_to_number(match, parse_float):
    if match.group(7):
        return parse_float(match.group(0))
    return int(match.group(0), 0)
