# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021 Taneli Hukkinen
# Licensed to PSF under a Contributor Agreement.

from datetime import date, datetime, time, timedelta, timezone, tzinfo
from functools import lru_cache
import re

RE_NUMBER = re.compile(
    r"""0(x[0-9A-Fa-f](_?[0-9A-Fa-f])*|b[01](_?[01])*|o[0-7](_?[0-7])*)|[+-]?(0|[1-9](_?[0-9])*)((\.[0-9](_?[0-9])*)?([eE][+-]?[0-9](_?[0-9])*)?)"""

)
RE_LOCALTIME = re.compile(r"([01][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])(?:\.([0-9]{1,6})[0-9]*)?")
RE_DATETIME = re.compile(
    # Micropython doesn't like the final ``?``
    r"""([0-9][0-9][0-9][0-9])-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])([Tt ]([01][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])(\.([0-9][0-9]?[0-9]?[0-9]?[0-9]?[0-9]?)[0-9]*)?(([Zz])|([+-])([01][0-9]|2[0-3]):([0-5][0-9]))?)?"""
)


def match_to_datetime(match):
    """Convert a `RE_DATETIME` match to `datetime.datetime` or `datetime.date`.

    Raises ValueError if the match does not correspond to a valid date
    or datetime.
    """
    (
        year_str,  # 1
        month_str,  # 2
        day_str,  # 3
        _,
        hour_str,  # 4
        minute_str,  # 5
        sec_str,  # 6
        _,
        micros_str,  # 7
        _,
        zulu_time,  # 8
        offset_sign_str,  # 9
        offset_hour_str,  # 10
        offset_minute_str,  # 11
    ) = match.groups()
    year, month, day = int(year_str), int(month_str), int(day_str)
    if hour_str is None:
        return date(year, month, day)
    hour, minute, sec = int(hour_str), int(minute_str), int(sec_str)
    micros = int(micros_str.ljust(6, "0")) if micros_str else 0
    if offset_sign_str:
        tz: tzinfo | None = cached_tz(
            offset_hour_str, offset_minute_str, offset_sign_str
        )
    elif zulu_time:
        tz = timezone.utc
    else:  # local date-time
        tz = None
    return datetime(year, month, day, hour, minute, sec, micros, tzinfo=tz)


@lru_cache(maxsize=None)
def cached_tz(hour_str, minute_str, sign_str):
    sign = 1 if sign_str == "+" else -1
    return timezone(
        timedelta(
            hours=sign * int(hour_str),
            minutes=sign * int(minute_str),
        )
    )


def match_to_localtime(match):
    hour_str, minute_str, sec_str, micros_str = match.groups()
    micros = int(micros_str.ljust(6, "0")) if micros_str else 0
    return time(int(hour_str), int(minute_str), int(sec_str), micros)


def match_to_number(match, parse_float):
    if match.group(7):
        return parse_float(match.group())
    return int(match.group(), 0)
