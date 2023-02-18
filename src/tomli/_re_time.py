from datetime import date, datetime, time, timedelta, timezone, tzinfo
import re

RE_LOCALTIME = re.compile(r"([01]\d|2[0-3]):([0-5]\d):([0-5]\d)(\.(\d\d?\d?\d?\d?\d?)\d*)?")

RE_DATETIME_YMD = re.compile(r"""(\d\d\d\d)-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])""")
RE_DATETIME_TIME = re.compile(
    r"""([Tt ]([01]\d|2[0-3]):([0-5]\d):([0-5]\d)(\.(\d\d?\d?\d?\d?\d?)\d*)?)?"""
)
RE_DATETIME_ZONE = re.compile(r"(([Zz])|([+-])([01]\d|2[0-3]):([0-5]\d))?")


def match_to_datetime(ymd_match, time_match, zone_match):
    """Convert a `RE_DATETIME` match to `datetime.datetime` or `datetime.date`.

    Raises ValueError if the match does not correspond to a valid date
    or datetime.
    """
    year_str = ymd_match.group(1)
    month_str = ymd_match.group(2)
    day_str = ymd_match.group(3)

    if time_match:
        hour_str = time_match.group(2)
        minute_str = time_match.group(3)
        sec_str = time_match.group(4)
        micros_str = time_match.group(6)
    else:
        hour_str = None
        minute_str = None
        sec_str = None
        micros_str = None

    if zone_match:
        zulu_time = zone_match.group(2)
        offset_sign_str = zone_match.group(3)
        offset_hour_str = zone_match.group(4)
        offset_minute_str = zone_match.group(5)
    else:
        zulu_time = None
        offset_sign_str = None
        offset_hour_str = None
        offset_minute_str = None

    year, month, day = int(year_str), int(month_str), int(day_str)
    if hour_str is None:
        return date(year, month, day)
    hour, minute, sec = int(hour_str), int(minute_str), int(sec_str)
    micros = int(micros_str.ljust(6, "0")) if micros_str else 0
    if offset_sign_str:
        tz = cached_tz(
            offset_hour_str, offset_minute_str, offset_sign_str
        )
    elif zulu_time:
        tz = timezone.utc
    else:  # local date-time
        tz = None
    return datetime(year, month, day, hour, minute, sec, micros, tzinfo=tz)


def lru_cache(func):
    cache = {}

    def wrapper(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result

    return wrapper


@lru_cache
def cached_tz(hour_str, minute_str, sign_str):
    sign = 1 if sign_str == "+" else -1
    return timezone(
        timedelta(
            hours=sign * int(hour_str),
            minutes=sign * int(minute_str),
        )
    )


def match_to_localtime(match):
    hour_str = match.group(1)
    minute_str = match.group(2)
    sec_str = match.group(3)
    micros_str = match.group(5)
    micros = int(micros_str + '0' * max(0, 6 - len(micros_str))) if micros_str else 0
    return time(int(hour_str), int(minute_str), int(sec_str), micros)
