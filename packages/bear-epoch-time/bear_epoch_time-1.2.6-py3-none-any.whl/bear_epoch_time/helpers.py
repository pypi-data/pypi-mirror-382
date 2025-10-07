"""A collection of helper functions for time conversion and formatting."""

from collections.abc import Callable
from datetime import timedelta
from inspect import BoundArguments, Signature, signature
from typing import TYPE_CHECKING, Any, ParamSpec, TypeVar

from bear_epoch_time.time_converter import TimeConverter

if TYPE_CHECKING:
    from bear_epoch_time import EpochTimestamp
    from bear_epoch_time.tz import TimeZoneType
ORD_DAY = "%Do"


def add_ord_suffix(number: int) -> str:
    """Add an ordinal suffix to a given number, usually used for dates or rankings.

    Parameters:
    number: int - The number to add an ordinal suffix to.

    Returns:
    str - The number with its ordinal suffix.
    """
    eleventh = 11
    thirteenth = 13
    suffix: str = ["th", "st", "nd", "rd", "th"][min(number % 10, 4)]
    if eleventh <= (number % 100) <= thirteenth:
        suffix = "th"
    return f"{number}{suffix}"


def format_interception(fmt: str, bound_args: BoundArguments) -> str:
    """Intercept and modify certain format strings before they are processed.

    Args:
        fmt (str): The original format string.
        bound_args (BoundArguments): The bound arguments from the calling function.

    Returns:
        str: The modified format string with ordinal day suffixes if applicable.
    """
    if ORD_DAY in fmt:
        self: EpochTimestamp | None = bound_args.arguments.get("self")
        if self is not None:
            tz: TimeZoneType = bound_args.arguments.get("tz") or self._tz
            day_in_tz: int = self.to_datetime.astimezone(tz).day
            return fmt.replace(ORD_DAY, f"{add_ord_suffix(day_in_tz)}")
    return fmt


T = TypeVar("T")
P = ParamSpec("P")


def fmt_parse(func: Callable[P, T]) -> Callable[P, T]:  # noqa: UP047
    """A decorator to intercept and modify format strings before passing them to the decorated function."""

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        sig: Signature = signature(func)
        bound_args: BoundArguments = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        fmt: str = bound_args.arguments.get("fmt", "")
        modified_fmt: str = format_interception(fmt, bound_args) if fmt else fmt  # Pass bound_args!
        bound_args.arguments["fmt"] = modified_fmt
        return func(*bound_args.args, **bound_args.kwargs)

    return wrapper


def convert_to_seconds(time_str: str) -> float:
    """Convert a time string to seconds.

    Args:
        time_str (str): A string representing time, e.g., "2h 30m 15s".

    Returns:
        float: The equivalent time in seconds.
    """
    return TimeConverter.parse_to_seconds(time_str)


def convert_to_milliseconds(time_str: str) -> float:
    """Convert a time string to milliseconds.

    Args:
        time_str (str): A string representing time, e.g., "1d 2h 3m 4s 500ms".

    Returns:
        float: The equivalent time in milliseconds.
    """
    return TimeConverter.parse_to_milliseconds(time_str)


def seconds_to_time(seconds: float, show_subseconds: bool = False) -> str:
    """Convert seconds to time string.

    Args:
        seconds (float): The number of seconds to convert.
        show_subseconds (bool): Whether to include subseconds in the output. Defaults to False.

    Returns:
        str: A human-readable time string.
    """
    return TimeConverter.format_seconds(seconds, show_subseconds)


def milliseconds_to_time(milliseconds: float) -> str:
    """Convert milliseconds to time string.

    Args:
        milliseconds (float): The number of milliseconds to convert.

    Returns:
        str: A human-readable time string.
    """
    return TimeConverter.format_milliseconds(milliseconds)


def seconds_to_timedelta(seconds: float) -> timedelta:
    """Convert seconds to timedelta. (Deprecated: use TimeConverter.to_timedelta)

    Args:
        seconds (float): The number of seconds to convert.

    Returns:
        timedelta: A timedelta object representing the duration.
    """
    return TimeConverter.to_timedelta(seconds)


def timedelta_to_seconds(td: timedelta | Any) -> float:
    """Convert timedelta to seconds.

    Args:
        td (timedelta | Any): A timedelta object to convert.

    Returns:
        float: The equivalent time in seconds.
    """
    return TimeConverter.from_timedelta(td)


__all__ = [
    "convert_to_milliseconds",
    "convert_to_seconds",
    "milliseconds_to_time",
    "seconds_to_time",
    "seconds_to_timedelta",
    "timedelta_to_seconds",
]
