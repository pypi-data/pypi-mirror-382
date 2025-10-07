"""A collection of helper functions and a TimeZoneHelper class for time zone conversions and manipulations."""

from contextlib import suppress
from datetime import datetime
from functools import cached_property, lru_cache
from typing import Any
from zoneinfo import ZoneInfo

from dateutil.tz import gettz
import pytz
from pytz.tzinfo import BaseTzInfo, DstTzInfo, StaticTzInfo
from tzlocal import get_localzone

PytzType = BaseTzInfo | DstTzInfo | StaticTzInfo
TimeZoneType = PytzType | ZoneInfo
TzInputType = str | TimeZoneType

UTC = ZoneInfo("UTC")


def get_local_timezone() -> ZoneInfo:
    """Get the local timezone using tzlocal and return it as a pytz timezone object.

    Returns:
        ZoneInfo: The local timezone as a ZoneInfo object. Defaults to UTC if unable to determine.
    """
    try:
        local_tz_str = str(get_localzone())
        return ZoneInfo(local_tz_str)
    except Exception:
        return UTC


class TimeZoneHelper:
    @cached_property
    def local_tz(self) -> ZoneInfo:
        """Get the local timezone as a ZoneInfo object.

        Returns:
            ZoneInfo: The local timezone. Defaults to UTC if unable to determine.
        """
        return get_local_timezone()

    @property
    def local_tz_dt(self) -> datetime:
        """Get the current datetime in the local timezone.

        Returns:
            datetime: The current datetime in the local timezone.
        """
        return datetime.now(tz=self.local_tz)

    @cached_property
    def all_timezones(self) -> list[str]:
        """Get a list of all available timezone names.

        Returns:
            list[str]: A list of all timezone names.
        """
        return pytz.all_timezones

    @property
    def tz_offset(self) -> int:
        """Get the current UTC offset in hours for the local timezone.

        Returns:
            int: The UTC offset in hours.
        """
        offset = self.local_tz_dt.utcoffset()
        if offset is None:
            return 0
        return int(offset.total_seconds() / 3600)

    def to_timezone(self, tz_input: TzInputType | None = None) -> ZoneInfo:
        """Convert various timezone inputs to a ZoneInfo timezone object.

        Args:
            tz_input: Can be a timezone string, a ZoneInfo object, or None.
                If None, defaults to UTC.

        Returns:
            ZoneInfo: A ZoneInfo timezone object. Defaults to UTC if input is None or unrecognized.

        Examples:
            >>> to_timezone("America/New_York")
            <ZoneInfo 'America/New_York'>

            >>> to_timezone("PST")
            <ZoneInfo 'America/Los_Angeles'>

            >>> to_timezone(None)
            <UTC>
        """
        if isinstance(tz_input, ZoneInfo):
            return tz_input

        if isinstance(tz_input, str):
            try:
                return ZoneInfo(tz_input)
            except Exception:
                try:
                    dateutil_tz: Any | None = gettz(tz_input)
                    if dateutil_tz is not None and hasattr(dateutil_tz, "zone"):
                        return ZoneInfo(dateutil_tz.zone)
                    # this means we have an abbreviation
                    pytz_tz = self.abbrev_to_tz(tz_input)
                    if pytz_tz:
                        return ZoneInfo(pytz_tz[0])

                    return UTC
                except Exception:
                    return UTC

        return UTC

    def convert(self, dt: datetime, target_tz: ZoneInfo) -> datetime:
        """Convert a datetime from one timezone to another.

        Args:
            dt (datetime): The datetime to convert (should be timezone-aware).
            target_tz: The target timezone.

        Returns:
            datetime: The datetime converted to the target timezone.

        Raises:
            ValueError: If the input datetime is naive.
        """
        if not self.is_aware(dt):
            raise ValueError("Input datetime must be timezone-aware")

        target_tz = self.to_timezone(target_tz)
        return dt.astimezone(target_tz)

    def is_aware(self, dt: datetime) -> bool:
        """Check if a datetime object is timezone-aware.

        Args:
            dt (datetime): The datetime to check.

        Returns:
            bool: True if timezone-aware, False if naive.
        """
        return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None

    def to_aware(self, dt: datetime, tz: TzInputType | None = None) -> datetime:
        """Make a naive datetime timezone-aware by adding timezone information.

        Args:
            dt (datetime): The naive datetime to make aware.
            tz: The timezone to apply. If None, uses UTC.

        Returns:
            datetime: A timezone-aware datetime or the original datetime if already aware.
        """
        if self.is_aware(dt):
            return dt

        return dt.replace(tzinfo=self.to_timezone(tz))

    @lru_cache(maxsize=128)  # noqa: B019
    def abbrev_to_tz(self, abbrev: str, region_hint: str = "America", date: datetime | None = None) -> list[str]:
        """Convert timezone abbreviation to full timezone name.

        Args:
            abbrev (str): The timezone abbreviation (e.g., "PDT").
            region_hint (str | None): Optional region hint to filter results (e.g., "America").
            date (datetime | None): A specific date to consider for DST. Defaults to current date if None.

        Returns:
            list[str]: A list of matching timezone names.
        """
        if date is None:
            date = self.local_tz_dt

        matches: list[str] = []

        for tz_name in self.all_timezones:
            with suppress(pytz.UnknownTimeZoneError):
                tz: PytzType = pytz.timezone(tz_name)
                localized: datetime = tz.localize(date) if date.tzinfo is None else date.astimezone(tz)

                if localized.strftime("%Z") == abbrev:
                    matches.append(tz_name)

        if region_hint:
            filtered: list[str] = [tz for tz in matches if region_hint.lower() in tz.lower()]
            return filtered if filtered else matches

        return matches


def convert_timezones(dt: datetime, target_tz: TzInputType | None = None) -> datetime:
    """Convert a datetime from one timezone to another.

    Args:
        dt (datetime): The datetime to convert (should be timezone-aware).
        target_tz: The target timezone. If None, defaults to UTC.

    Returns:
        datetime: The datetime converted to the target timezone.

    Raises:
        ValueError: If the input datetime is naive.
    """
    tz_helper = TimeZoneHelper()
    return tz_helper.convert(dt, tz_helper.to_timezone(target_tz))


def is_aware(dt: datetime) -> bool:
    """Check if a datetime object is timezone-aware.

    Args:
        dt (datetime): The datetime to check.

    Returns:
        bool: True if timezone-aware, False if naive.
    """
    tz_helper = TimeZoneHelper()
    return tz_helper.is_aware(dt)


def to_timezone(tz_input: TzInputType | None = None) -> ZoneInfo:
    """Convert various timezone inputs to a ZoneInfo timezone object.

    Args:
        tz_input: Can be a timezone string, a ZoneInfo object, or None.
            If None, defaults to UTC.

    Returns:
        ZoneInfo: A ZoneInfo timezone object. Defaults to UTC if input is None or unrecognized.

    Examples:
        >>> to_timezone("America/New_York")
        <ZoneInfo 'America/New_York'>

        >>> to_timezone("PST")
        <ZoneInfo 'America/Los_Angeles'>

        >>> to_timezone(None)
        <UTC>
    """
    tz_helper = TimeZoneHelper()
    return tz_helper.to_timezone(tz_input)


__all__ = ["TimeZoneType", "TimeZoneType", "convert_timezones", "get_local_timezone", "is_aware"]


if __name__ == "__main__":
    tz_helper = TimeZoneHelper()
    print("Local Timezone:", tz_helper.local_tz)
    print("Current Local Time:", tz_helper.local_tz_dt)

    ex1 = "America/Los_Angeles"
    ex2 = "PDT"
    ex3 = None

    print(f"Convert '{ex1}':", tz_helper.to_timezone(ex1))  # should be ZoneInfo('America/Los_Angeles')
    print(f"Convert '{ex2}':", tz_helper.to_timezone(ex2))  # should be ZoneInfo('America/Los_Angeles') or similar
    print(f"Convert '{ex3}':", tz_helper.to_timezone(ex3))  # should be ZoneInfo("UTC")
