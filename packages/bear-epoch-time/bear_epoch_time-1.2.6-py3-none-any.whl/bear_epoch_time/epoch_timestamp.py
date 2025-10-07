"""EpochTimestamp Class for handling epoch time in seconds or milliseconds.

This class provides methods to convert between epoch time and human-readable formats, including datetime objects and formatted strings.
"""

# where are deltatime objects?
from datetime import date as dt_date, datetime, time as dt_time, timedelta
from functools import cached_property
from typing import ClassVar, Literal, Self, overload

from bear_epoch_time.constants import DATE_FORMAT, DT_FORMAT_WITH_TZ, PT_TIME_ZONE, TIME_FORMAT, UTC, neg
from bear_epoch_time.helpers import fmt_parse
from bear_epoch_time.time_converter import TimeConverter, from_timedelta, time_to_seconds
from bear_epoch_time.tz import TimeZoneHelper, TimeZoneType

ReprChoices = Literal["int", "object", "datetime"]
Operators = Literal["mult", "div"]
Mult = Literal[1000, 1]


@fmt_parse
def fmt_convert(fmt: str) -> str:
    """A decorator to intercept and modify format strings before passing them to the decorated function."""
    return fmt


class EpochTimestamp(int):
    """Custom class to represent epoch timestamps.

    Inherits from int to allow direct arithmetic operations.
    This class is used to represent time in seconds or milliseconds since the epoch (1970-01-01 00:00:00 UTC)
    with it defaulting to ms since that is the most common use case.

    Default value is the current epoch time in milliseconds. It is suggested to set the value to 0 if using it as
    a placeholder value or call `now()` to get the current epoch time.
    """

    _repr_style: ClassVar[ReprChoices] = "int"
    """Three choices: int, object, or datetime.
    Int is the default and is the most common use case.
    Object will return the object representation of the class.
    Datetime will return a human readable timestamp like ``10-01-2025.`` """
    _datefmt: ClassVar[str] = fmt_convert(DATE_FORMAT)
    """The format of the default date string. Default is ``%m-%d-%Y``."""
    _timefmt: ClassVar[str] = TIME_FORMAT
    """The format of the default time string. Default is ``%I:%M %p``."""
    _fullfmt: ClassVar[str] = fmt_convert(DT_FORMAT_WITH_TZ)
    """The format of the default datetime string. Default is ``%m-%d-%Y %I:%M %p %Z``."""
    _tz: ClassVar[TimeZoneType] = PT_TIME_ZONE
    """The default timezone for the class. Default is ``America/Los_Angeles``."""
    _local_tz_helper: ClassVar[TimeZoneHelper | None] = None
    """A cached TimeZoneHelper instance for local timezone operations."""
    # region Class Methods

    @classmethod
    def tz_helper(cls) -> TimeZoneHelper:
        """Get a cached TimeZoneHelper instance for local timezone operations.

        Returns:
            TimeZoneHelper: A cached TimeZoneHelper instance.
        """
        if cls._local_tz_helper is None:
            cls._local_tz_helper = TimeZoneHelper()
        return cls._local_tz_helper

    @classmethod
    def set_repr_style(cls, repr_style: ReprChoices) -> None:
        """Set the plain representation of the class.

        Args:
            repr_style (str): The representation style ("int", "object", or "datetime")
        """
        cls._repr_style = repr_style

    @classmethod
    def set_date_format(cls, datefmt: str) -> None:
        """Set the default date format for the class.

        Args:
            datefmt (str): The format of the date string. Default is "%m-%d-%Y".
        """
        cls._datefmt = datefmt

    @classmethod
    def set_time_format(cls, timefmt: str) -> None:
        """Set the default time format for the class.

        Args:
            timefmt (str): The format of the time string. Default is "%I:%M %p".
        """
        cls._timefmt = timefmt

    @classmethod
    def set_full_format(cls, fullfmt: str) -> None:
        """Set the default datetime format for the class.

        Args:
            fullfmt (str): The format of the datetime string. Default is "%m-%d-%Y %I:%M %p %Z".
        """
        cls._fullfmt = fullfmt

    @classmethod
    def set_timezone(cls, tz: TimeZoneType) -> None:
        """Set the default timezone for the class.

        Args:
            tz (TimeZoneType): The timezone to set. Default is PT_TIME_ZONE.
        """
        cls._tz = tz

    @classmethod
    def now(cls, milliseconds: bool = True) -> Self:
        """Get the current epoch time in milliseconds or seconds in UTC.

        Args:
            milliseconds (bool): If True, return milliseconds. If False, return seconds. Default is True for milliseconds.

        Returns:
            EpochTimestamp: The current epoch time.
        """
        return cls(cls.op(v=datetime.now(UTC).timestamp(), ms=milliseconds), milliseconds=milliseconds)

    @classmethod
    def from_seconds(cls, seconds: int, milliseconds: bool = True) -> Self:
        """Create an EpochTimestamp from seconds

        Args:
            seconds (int): The number of seconds since the epoch.

        Returns:
            EpochTimestamp: The epoch timestamp in seconds.
        """
        return cls(int(cls.op(seconds, ms=milliseconds)), milliseconds=milliseconds)

    @classmethod
    def from_datetime(cls, dt: datetime, milliseconds: bool = True) -> Self:
        """Convert a datetime object to an epoch timestamp.

        Args:
            dt (datetime): The datetime object to convert.
            milliseconds (bool): If True, return milliseconds. If False, return seconds.

        Returns:
            EpochTimestamp: The epoch timestamp in milliseconds or seconds based on the milliseconds argument.
        """
        helper: TimeZoneHelper = cls.tz_helper()
        local_tz: TimeZoneType = helper.local_tz
        if not helper.is_aware(dt):
            dt = dt.replace(tzinfo=UTC)
        return cls(cls.op(dt.astimezone(local_tz).timestamp(), ms=milliseconds), milliseconds=milliseconds)

    @classmethod
    @fmt_parse
    def from_dt_string(
        cls,
        dt_string: str,
        milliseconds: bool = True,
        fmt: str | None = None,
        tz: TimeZoneType | str | None = None,
    ) -> Self:
        """Convert a datetime string to an epoch timestamp

        Args:
            dt_string (str): The datetime string to convert.
            milliseconds (bool): If True, return milliseconds. If False, return seconds.
            fmt (str): The format of the datetime string. Default is "%m-%d-%Y %I:%M %p".

        Returns:
            EpochTimestamp: The epoch timestamp in milliseconds or seconds based on the milliseconds argument.
        """
        helper: TimeZoneHelper = cls.tz_helper()
        tz = helper.to_timezone(tz) if tz else cls._tz
        dt: datetime = datetime.strptime(dt_string, fmt if fmt else cls._fullfmt).replace(tzinfo=tz)
        t: int = cls.op(v=dt.astimezone(tz=UTC).timestamp(), ms=milliseconds)
        return cls(t, milliseconds=milliseconds)

    @classmethod
    def from_iso_string(cls, iso_string: str, milliseconds: bool = True) -> Self:
        """Convert an ISO 8601 datetime string to an epoch timestamp.

        Args:
            iso_string (str): The ISO 8601 datetime string to convert.
            milliseconds (bool): If True, return milliseconds. If False, return seconds.

        Returns:
            EpochTimestamp: The epoch timestamp in milliseconds or seconds based on the milliseconds argument.
        """
        return cls.from_datetime(datetime.fromisoformat(iso_string), milliseconds=milliseconds)

    @overload
    @classmethod
    def op(cls, v: float, ms: bool, op: Operators = "mult", to_int: Literal[True] = True) -> int: ...
    @overload
    @classmethod
    def op(cls, v: float, ms: bool, op: Operators = "mult", to_int: Literal[False] = False) -> float: ...

    @classmethod
    def op(cls, v: float, ms: bool, op: Operators = "mult", to_int: bool = True) -> float | int:
        """Multiply the value by 1000 if milliseconds is True, else return the value as is.

        Args:
            v (float): The value to multiply.
            ms (bool): If True, multiply by 1000. If False, return the value as is.
            op (Operators): The operation to perform. Default is "mult".
            to_int (bool): If True, return the result as an integer. If False, return as a float. Default is True.

        Returns:
            float | int: The multiplied value if to_int is False, else the integer value.
        """
        mult: Mult = 1000 if ms else 1
        value: float | None = v * mult if op == "mult" else v / mult if op == "div" else None
        if value is None:
            raise ValueError(f"Invalid operation: {op}. Use 'mult' or 'div'.")
        return int(value) if to_int else float(value)

    def __new__(cls, value: int | None = None, milliseconds: bool = True) -> Self:
        """Create a new EpochTimestamp instance."""
        value = value if value is not None else cls.now(milliseconds)
        return super().__new__(cls, value)

    # endregion

    # region Instance Methods

    def __str__(self) -> str:
        return int.__str__(self)

    def __repr__(self) -> str:
        if self.is_default:
            return "EpochTimestamp(0) (Default Value)"
        match self._repr_style:
            case "int":
                return f"{int(self)}"
            case "object":
                return f"EpochTimestamp({int(self)})"
            case "datetime":
                return f"{self.to_datetime.strftime(self._datefmt)}"
            case _:
                raise ValueError(f"Invalid repr style: {self._repr_style}")

    def __init__(self, value: int | None = None, milliseconds: bool = True) -> None:  # noqa: ARG002
        """Initialize the EpochTimestamp instance."""
        self.milliseconds: bool = milliseconds

    @fmt_parse
    def to_string(self, fmt: str | None = None, tz: TimeZoneType | None = None) -> str:
        """Convert the epoch timestamp to a formatted string, taking into account the timezone and format.

        Args:
            fmt (str): The format of the datetime string. Default is "%m-%d-%Y %I:%M %p".
            tz (TimeZoneType | None): The timezone to convert to. Default is PT_TIME_ZONE.

        Returns:
            str: The formatted date string.
        """
        if self.is_default:
            raise ValueError("Cannot convert default value to string.")
        fmt = fmt if fmt else self._fullfmt
        tz = tz if tz else self._tz
        return self.to_datetime.astimezone(tz).strftime(fmt)

    @fmt_parse
    def date_str(self, fmt: str | None = None, tz: TimeZoneType | None = None) -> str:
        """Convert the epoch timestamp to a date string in the format "%m-%d-%Y".

        Args:
            tz (TimeZoneType | None): The timezone to convert to. Default is PT_TIME_ZONE.

        Returns:
            str: The formatted date string.
        """
        return self.to_string(
            fmt=fmt if fmt is not None else self._datefmt,
            tz=tz if tz is not None else self._tz,
        )

    @fmt_parse
    def time_str(self, fmt: str | None = None, tz: TimeZoneType | None = None) -> str:
        """Convert the epoch timestamp to a time string in the format "%I:%M %p".

        Args:
            tz (TimeZoneType | None): The timezone to convert to. Default is PT_TIME_ZONE.

        Returns:
            str: The formatted time string.
        """
        return self.to_string(
            fmt=fmt if fmt is not None else self._timefmt,
            tz=tz if tz is not None else self._tz,
        )

    def add_timedelta(
        self,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        milliseconds: int = 0,
        delta: timedelta = timedelta(seconds=0),
    ) -> Self:
        """Add a timedelta to the epoch timestamp.

        If you pass negative values, you will create a negative timedelta.

        Args:
            days (int): The number of days to add. Default is 0.
            hours (int): The number of hours to add. Default is 0.
            minutes (int): The number of minutes to add. Default is 0.
            seconds (int): The number of seconds to add. Default is 0.
            milliseconds (int): The number of milliseconds to add. Default is 0.
            delta (timedelta): A timedelta object to add. Default is timedelta(0).

        Returns:
            EpochTimestamp: The new epoch timestamp after adding the timedelta.
        """
        secs = time_to_seconds(days, hours, minutes, seconds, milliseconds)
        secs += from_timedelta(delta)
        new_timestamp: int = self.op(v=(self.to_seconds + secs), ms=self.milliseconds)
        return type(self)(new_timestamp)

    def start_of_day(self, tz: TimeZoneType | None = None) -> Self:
        """Get the start of the day for the epoch timestamp, defaults to midnight of the day in UTC.

        Args:
            tz (TimeZoneType | None): The timezone to convert to. Will default to UTC if not provided.

        Returns:
            EpochTimestamp: The epoch timestamp at the start of the day.
        """
        dt: datetime = self.to_datetime.astimezone(tz) if tz else self.to_datetime
        dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        return type(self).from_datetime(dt, milliseconds=self.milliseconds)

    def end_of_day(self, tz: TimeZoneType | None = None) -> Self:
        """Get the end of the day for the epoch timestamp, defaults to 23:59:59.999999 of the day in UTC.

        Args:
            tz (TimeZoneType | None): The timezone to convert to. Will default to UTC if not provided.

        Returns:
            EpochTimestamp: The epoch timestamp at the end of the day.
        """
        dt: datetime = self.to_datetime.astimezone(tz) if tz else self.to_datetime
        dt = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
        return type(self).from_datetime(dt, milliseconds=self.milliseconds)

    def time_since(self, other: Self, unit: Literal["M", "d", "h", "m", "s", "ms"] = "d") -> float:
        """Calculate the time difference between this timestamp and another in the specified unit.

        Args:
            other (EpochTimestamp): The other epoch timestamp to compare with.
            unit (str): The unit to return ("M", "d", "h", "m", "s", "ms"). Default is "d" for days.

        Returns:
            float: The time difference in the specified unit.
        """
        return TimeConverter.time_since(int(self.to_seconds), int(other.to_seconds), unit)

    def since(self, other: Self, milliseconds: bool = True) -> Self:
        """Calculate the time difference between this timestamp and another in seconds or milliseconds.

        Args:
            other (EpochTimestamp): The other epoch timestamp to compare with.
            milliseconds (bool): If True, return the difference in milliseconds. If False, return in seconds. Default is False.

        Returns:
            EpochTimestamp: The time difference as an EpochTimestamp.
        """
        t: int = self.op(v=abs(self.to_seconds - other.to_seconds), ms=milliseconds)
        return type(self)(t, milliseconds=milliseconds)

    # endregion

    # region Properties

    @property
    def to_datetime(self) -> datetime:
        """Convert the epoch timestamp to a datetime object in UTC.

        Returns:
            datetime: The datetime representation of the epoch timestamp.
        """
        t: float = self.op(v=self, ms=self.milliseconds, op="div", to_int=False)
        return datetime.fromtimestamp(t, tz=UTC)

    @property
    def to_iso(self) -> str:
        """Get the ISO 8601 string representation of the epoch timestamp.

        Returns:
            str: The ISO 8601 formatted string.
        """
        return self.to_datetime.isoformat()

    @property
    def to_seconds(self) -> int:
        """Get the total seconds from the epoch timestamp (truncated to whole seconds).

        If the timestamp is in milliseconds, it converts it to seconds by truncating
        the millisecond portion, else just returns the integer value.

        Returns:
            int: The total whole seconds since the epoch.
        """
        return int(self.op(v=self, ms=self.milliseconds, op="div", to_int=False))

    @property
    def to_milliseconds(self) -> int:
        """Get the total milliseconds from the epoch timestamp.

        If the timestamp is in seconds, it converts it to milliseconds else
        just returns the integer value.

        Returns:
            int: The total milliseconds since the epoch.
        """
        return self.op(v=self, ms=not self.milliseconds, op="mult", to_int=True)

    @property
    def to_int(self) -> int:
        """Converts the epoch timestamp to an integer value. Mostly used for type hinting since this *IS* an int.

        Returns:
            int: The total milliseconds since the epoch.
        """
        return int(self)

    @property
    def to_duration(self) -> str:
        """The duration string representation of the epoch timestamp.

        In other words, this is the duration since the epoch (1970-01-01 00:00:00 UTC) in a human-readable format
        like "675M 28d 2h 12m 28s".

        Returns:
            str: The formatted duration string.
        """
        return TimeConverter.format_seconds(self.to_seconds, show_subseconds=True)

    @property
    def date(self) -> dt_date:
        """Get the date part of the epoch timestamp.

        Returns:
            date: The date part of the epoch timestamp.
        """
        return self.to_datetime.date()

    @property
    def time(self) -> dt_time:
        """Get the time part of the epoch timestamp.

        Returns:
            time: The time part of the epoch timestamp as a time object.
        """
        return self.to_datetime.time()

    @property
    def hour(self) -> int:
        """Get the hour from the epoch timestamp.

        Returns:
            int: The hour of the epoch timestamp.
        """
        return self.to_datetime.hour

    @property
    def minute(self) -> int:
        """Get the minute from the epoch timestamp.

        Returns:
            int: The minute of the epoch timestamp.
        """
        return self.to_datetime.minute

    @property
    def second(self) -> int:
        """Get the second from the epoch timestamp.

        Returns:
            int: The second of the epoch timestamp.
        """
        return self.to_datetime.second

    @property
    def year(self) -> int:
        """Get the year from the epoch timestamp.

        Returns:
            int: The year of the epoch timestamp.
        """
        return self.to_datetime.year

    @property
    def month(self) -> int:
        """Get the month from the epoch timestamp.

        Returns:
            int: The month of the epoch timestamp.
        """
        return self.to_datetime.month

    @property
    def day(self) -> int:
        """Get the day from the epoch timestamp.

        Returns:
            int: The day of the epoch timestamp.
        """
        return self.to_datetime.day

    @property
    def week(self) -> int:
        """Get the ISO week number from the epoch timestamp.

        Returns:
            int: The ISO week number (1-53).
        """
        return self.to_datetime.isocalendar().week

    @property
    def day_of_week(self) -> int:
        """Get the day of the week from the epoch timestamp.

        Returns:
            int: The day of the week (0=Monday, 6=Sunday).
        """
        return self.to_datetime.weekday()

    @property
    def day_of_year(self) -> int:
        """Get the day of the year from the epoch timestamp.

        Returns:
            int: The day of the year (1-366).
        """
        return self.to_datetime.timetuple().tm_yday

    @property
    def iso_weekday(self) -> int:
        """Get the ISO day of the week from the epoch timestamp.

        Returns:
            int: The ISO day of the week (1=Monday, 7=Sunday).
        """
        return self.to_datetime.isoweekday()

    @property
    def day_name(self) -> str:
        """Get the day name from the epoch timestamp.

        Returns:
            str: The full name of the day of the epoch timestamp like "Monday".
        """
        return self.to_datetime.strftime("%A")

    @property
    def month_name(self) -> str:
        """Get the month name from the epoch timestamp.

        Returns:
            str: The full name of the month of the epoch timestamp.
        """
        return self.to_datetime.strftime("%B")

    @property
    def is_default(self) -> bool:
        """Check if the timestamp is zero, this is useful since zero can be a placeholder value.

        Returns:
            bool: True if the timestamp is zero, False otherwise.
        """
        return self == 0

    def __eq__(self, other: object) -> bool:
        if isinstance(other, EpochTimestamp):
            return int(self) == int(other)
        if isinstance(other, datetime):
            return self.to_datetime == other
        if isinstance(other, (int | float)):
            return int(self) == int(other)
        if isinstance(other, (dt_date)):
            return self.date == other
        if isinstance(other, (dt_time)):
            return self.time == other
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        if isinstance(other, EpochTimestamp):
            return int(self) < int(other)
        if isinstance(other, datetime):
            return self.to_datetime < other
        if isinstance(other, (int | float)):
            return int(self) < int(other)
        if isinstance(other, (dt_date)):
            return self.date < other
        if isinstance(other, (dt_time)):
            return self.time < other
        return NotImplemented

    def __le__(self, other: object) -> bool:
        if isinstance(other, EpochTimestamp):
            return int(self) <= int(other)
        if isinstance(other, datetime):
            return self.to_datetime <= other
        if isinstance(other, (int | float)):
            return int(self) <= int(other)
        if isinstance(other, (dt_date)):
            return self.date <= other
        if isinstance(other, (dt_time)):
            return self.time <= other
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        if isinstance(other, EpochTimestamp):
            return int(self) > int(other)
        if isinstance(other, datetime):
            return self.to_datetime > other
        if isinstance(other, (int | float)):
            return int(self) > int(other)
        if isinstance(other, (dt_date)):
            return self.date > other
        if isinstance(other, (dt_time)):
            return self.time > other
        return NotImplemented

    def __ge__(self, other: object) -> bool:
        if isinstance(other, EpochTimestamp):
            return int(self) >= int(other)
        if isinstance(other, datetime):
            return self.to_datetime >= other
        if isinstance(other, (int | float)):
            return int(self) >= int(other)
        if isinstance(other, (dt_date)):
            return self.date >= other
        if isinstance(other, (dt_time)):
            return self.time >= other
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        if isinstance(other, EpochTimestamp):
            return int(self) != int(other)
        if isinstance(other, datetime):
            return self.to_datetime != other
        if isinstance(other, (int | float)):
            return int(self) != int(other)
        if isinstance(other, (dt_date)):
            return self.date != other
        if isinstance(other, (dt_time)):
            return self.time != other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(int(self))

    @cached_property
    def _get_template_vars(self) -> dict[str, str]:
        """Get template variables for string formatting."""
        return {
            "epoch": str(self),
            "seconds": str(self.to_seconds),
            "milliseconds": str(self.to_milliseconds),
            "iso": self.to_iso,
            "date": self.date_str(),
            "time": self.time_str(),
            "datetime": self.to_datetime.strftime(self._fullfmt),
            "year": str(self.year),
            "month": str(self.month),
            "week": str(self.week),
            "isoweekday": str(self.iso_weekday),
            "day": str(self.day),
            "hour": str(self.hour),
            "minute": str(self.minute),
            "day_of_week": str(self.day_of_week),
            "day_of_year": str(self.day_of_year),
            "month_name": self.month_name,
            "day_name": self.day_name,
        }

    def format(self, template: str) -> str:
        """Format the epoch timestamp using template variables.

        Template variables like $iso, $date, $time, etc. are substituted first,
        then the result can contain strftime patterns for final formatting.

        Args:
            template: Template string with $variables and/or strftime patterns

        Returns:
            Formatted string

        Examples:
            timestamp.format("$iso")  # ISO format
            timestamp.format("$date at $time")  # Custom combination
            timestamp.format("Event: $datetime")  # Descriptive template
        """
        if self.is_default:
            raise ValueError("Cannot format default value.")

        from string import Template  # noqa: PLC0415

        substituted: str = Template(template).substitute(self._get_template_vars)
        if "%" in substituted:  # If result looks like a strftime pattern, apply it
            return self.to_datetime.strftime(substituted)
        return substituted

    # endregion


if __name__ == "__main__":
    # ts: EpochTimestamp = EpochTimestamp(1757191982631)
    # ts2 = EpochTimestamp.now()
    # string: str = ts.to_string(fmt="%A, %B %Do %Y, %I:%M:%S %p")
    # string2 = ts2.to_string(fmt="%A, %B %Do %Y, %I:%M:%S %p")

    # print(string)
    # print(string2)
    ts: EpochTimestamp = EpochTimestamp().now()
    new_ts: EpochTimestamp = ts.add_timedelta(days=neg(1))

    print(new_ts.to_string())
