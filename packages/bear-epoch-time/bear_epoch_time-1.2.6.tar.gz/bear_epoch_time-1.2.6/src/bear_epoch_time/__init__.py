"""This module provides tools for working with epoch time, including"""

from importlib.metadata import version

from .constants import (
    DATE_FORMAT,
    DATE_TIME_FORMAT,
    DAY_AGO,
    DAY_AGO_SECS,
    DAYS_IN_MONTH,
    DT_FORMAT_WITH_SECONDS,
    ET_TIME_ZONE,
    HOURS_IN_DAY,
    MILLISECONDS_IN_SECOND,
    PT_TIME_ZONE,
    SECONDS_IN_DAY,
    SECONDS_IN_HOUR,
    SECONDS_IN_MINUTE,
    SECONDS_IN_MONTH,
    TIME_FORMAT,
    TIME_FORMAT_WITH_SECONDS,
    UTC,
    neg,
)
from .epoch_timestamp import EpochTimestamp
from .helpers import (
    add_ord_suffix,
    convert_to_milliseconds,
    convert_to_seconds,
    milliseconds_to_time,
    seconds_to_time,
    timedelta_to_seconds,
)
from .time_converter import TimeConverter
from .time_tools import TimeTools
from .timer import TimerData, async_timer, create_async_timer, create_timer, timer

__version__: str = version("bear-epoch-time")

__all__ = [
    "DATE_FORMAT",
    "DATE_TIME_FORMAT",
    "DAYS_IN_MONTH",
    "DAY_AGO",
    "DAY_AGO_SECS",
    "DT_FORMAT_WITH_SECONDS",
    "ET_TIME_ZONE",
    "HOURS_IN_DAY",
    "MILLISECONDS_IN_SECOND",
    "PT_TIME_ZONE",
    "SECONDS_IN_DAY",
    "SECONDS_IN_HOUR",
    "SECONDS_IN_MINUTE",
    "SECONDS_IN_MONTH",
    "TIME_FORMAT",
    "TIME_FORMAT_WITH_SECONDS",
    "UTC",
    "EpochTimestamp",
    "TimeConverter",
    "TimeTools",
    "TimerData",
    "__version__",
    "add_ord_suffix",
    "async_timer",
    "convert_to_milliseconds",
    "convert_to_seconds",
    "create_async_timer",
    "create_timer",
    "milliseconds_to_time",
    "neg",
    "seconds_to_time",
    "timedelta_to_seconds",
    "timer",
]
