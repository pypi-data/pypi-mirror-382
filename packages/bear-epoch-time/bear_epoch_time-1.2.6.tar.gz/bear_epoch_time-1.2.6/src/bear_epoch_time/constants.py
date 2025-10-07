"""Constants for the Bear Epoch Time package."""

from datetime import timedelta
from typing import Literal, LiteralString, overload
from zoneinfo import ZoneInfo


@overload
def neg(value: int) -> int: ...


@overload
def neg(value: float) -> float: ...


def neg(value: float) -> float | int:
    """Indicate that a value is negative.

    Args:
        value (float | int): The value to negate.

    Returns:
        float | int: The negated value.
    """
    return -abs(value)


# Time Zones #

UTC = ZoneInfo("UTC")
"""UTC timezone, a UTC timezone using a ZoneInfo timezone object"""

PT_TIME_ZONE = ZoneInfo("America/Los_Angeles")
"""A Pacific Time Zone using a ZoneInfo timezone object"""

ET_TIME_ZONE = ZoneInfo("America/New_York")
"""Eastern Time Zone using a ZoneInfo timezone object"""

# Date and Time Formats #

DATE_FORMAT = "%m-%d-%Y"
"""Date format"""

TIME_FORMAT = "%I:%M %p"
"""Time format with 12 hour format"""

TIME_FORMAT_WITH_SECONDS = "%I:%M:%S %p"
"""Time format with 12 hour format and seconds"""

DATE_TIME_FORMAT: LiteralString = f"{DATE_FORMAT} {TIME_FORMAT}"
"""Datetime format with 12 hour format"""

DT_FORMAT_WITH_SECONDS: LiteralString = f"{DATE_FORMAT} {TIME_FORMAT_WITH_SECONDS}"
"""Datetime format with 12 hour format and seconds"""

DT_FORMAT_WITH_TZ: LiteralString = f"{DATE_TIME_FORMAT} %Z"
"""Datetime format with 12 hour format and timezone"""

DT_FORMAT_WITH_TZ_AND_SECONDS: LiteralString = f"{DT_FORMAT_WITH_SECONDS} %Z"
"""Datetime format with 12 hour format, seconds, and timezone"""

# Time Related Constants #

MILLISECONDS_IN_SECOND: Literal[1000] = 1000
"""1000 milliseconds in a second"""

SECONDS_IN_MINUTE: Literal[60] = 60
"""60 seconds in a minute"""

MINUTES_IN_HOUR: Literal[60] = 60
"""60 minutes in an hour"""

HOURS_IN_DAY: Literal[24] = 24
"""24 hours in a day"""

DAYS_IN_MONTH: Literal[30] = 30
"""30 days in a month, approximation for a month"""

SECONDS_IN_HOUR: Literal[3600] = SECONDS_IN_MINUTE * MINUTES_IN_HOUR
"""60 * 60 = 3600 seconds in an hour"""

SECONDS_IN_DAY: Literal[86400] = SECONDS_IN_HOUR * HOURS_IN_DAY
"""24 * 60 * 60 = 86400 seconds in a day"""

SECONDS_IN_MONTH: Literal[2592000] = SECONDS_IN_DAY * DAYS_IN_MONTH
"""30 * 24 * 60 * 60 = 2592000 seconds in a month"""

DAY_AGO_SECS: int = neg(SECONDS_IN_DAY)
"""Negative number of seconds in a day, useful for calculations"""

DAY_AGO = timedelta(seconds=DAY_AGO_SECS)
"""A timedelta representing 24 hours ago"""
