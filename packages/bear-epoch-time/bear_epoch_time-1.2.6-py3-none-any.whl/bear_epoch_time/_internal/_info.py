from contextlib import suppress
from dataclasses import dataclass, field
from importlib.metadata import PackageMetadata, PackageNotFoundError, distribution, version
from typing import Any, Literal

from bear_epoch_time._internal._version import __commit_id__, __version__, __version_tuple__


@dataclass
class _Package:
    """Dataclass to store package information."""

    name: str
    """Package name."""
    version: str = "0.0.0"
    """Package version."""
    description: str = "No description available."
    """Package description."""

    def __str__(self) -> str:
        """String representation of the package information."""
        return f"{self.name} v{self.version}: {self.description}"


def _get_version(dist: str = "bear-epoch-time") -> str:
    """Get version of the given distribution or the current package.

    Parameters:
        dist: A distribution name.

    Returns:
        A version number.
    """
    try:
        return version(dist)
    except PackageNotFoundError:
        return "0.0.0"


def _get_package_info(dist: str = "bear-epoch-time") -> _Package:
    """Get package information for the given distribution.

    Parameters:
        dist: A distribution name.

    Returns:
        Package information with version, name, and description.
    """
    return _Package(name=dist, version=_get_version(dist), description=_get_description(dist))


def _get_description(dist: str = "bear-epoch-time") -> str:
    """Get description of the given distribution or the current package.

    Parameters:
        dist: A distribution name.

    Returns:
        A description string.
    """
    try:
        dis: PackageMetadata = distribution(dist).metadata
        return dis.get("Summary", "No description available.")  # type: ignore[arg-type]
    except PackageNotFoundError:
        return "No description available."


@dataclass(slots=True, frozen=True)
class _ProjectName:
    """A class to represent the project name and its metadata as literals for type safety.

    This is done this way to make it easier to see the values in the IDE and to ensure that the values are consistent throughout the codebase.
    """

    package_distribution: Literal["bear-epoch-time"] = "bear-epoch-time"
    project: Literal["bear_epoch_time"] = "bear_epoch_time"
    project_upper: Literal["BEAR_EPOCH_TIME"] = "BEAR_EPOCH_TIME"
    env_variable: Literal["BEAR_EPOCH_TIME_ENV"] = "BEAR_EPOCH_TIME_ENV"


@dataclass(slots=True)
class _ProjectVersion:
    """A class to represent the project version."""

    string: str = field(default="")
    tuple_: tuple[int, int, int] = field(default=(0, 0, 0))
    commit_id: str = field(default=__commit_id__)

    def __post_init__(self) -> None:
        """Post-initialization to validate and set default values."""
        self.string = self.validate_version(self.string)
        self.tuple_ = self.validate_version_tuple(self.tuple_)

    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate the version string."""
        if not isinstance(v, str) or "0.0.0" in v:
            with suppress(PackageNotFoundError):
                return _get_version("bear-epoch-time")
            return "0.0.0"
        return v

    @classmethod
    def validate_version_tuple(cls, v: Any) -> tuple[int, int, int]:
        """Validate the version tuple."""
        parts = 3
        if not isinstance(v, tuple) or v == (0, 0, 0):
            with suppress(Exception):
                value: str = _get_version("bear-epoch-time")
                v = tuple(int(x) for x in value.split(".") if x.isdigit())
                if len(v) == parts:
                    return v
            return (0, 0, 0)
        return v


@dataclass(frozen=True, slots=True)
class _ProjectMetadata:
    """Dataclass to store the current project metadata."""

    _version: _ProjectVersion
    name_: _ProjectName = field(default_factory=_ProjectName)

    def __str__(self) -> str:
        """String representation of the project metadata."""
        return f"{self.full_version}: {self.description}"

    @property
    def version(self) -> str:
        """Get the project version as a string."""
        return self._version.string

    @property
    def version_tuple(self) -> tuple[int, int, int]:
        """Get the project version as a tuple."""
        return self._version.tuple_

    @property
    def commit_id(self) -> str:
        """Get the Git commit ID of the current version."""
        return self._version.commit_id

    @property
    def full_version(self) -> str:
        """Get the full version string."""
        return f"{self.name} v{self._version.string}"

    @property
    def description(self) -> str:
        """Get the project description from the distribution metadata."""
        return _get_description(self.name)

    @property
    def name(self) -> Literal["bear-epoch-time"]:
        """Get the package distribution name."""
        return self.name_.package_distribution

    @property
    def name_upper(self) -> Literal["BEAR_EPOCH_TIME"]:
        """Get the project name in uppercase with underscores."""
        return self.name_.project_upper

    @property
    def project_name(self) -> Literal["bear_epoch_time"]:
        """Get the project name."""
        return self.name_.project

    @property
    def env_variable(self) -> Literal["BEAR_EPOCH_TIME_ENV"]:
        """Get the environment variable name for the project.

        Used to check if the project is running in a specific environment.
        """
        return self.name_.env_variable


METADATA = _ProjectMetadata(
    _version=_ProjectVersion(
        string=__version__ if __version__ != "0.0.0" else _get_version("bear-epoch-time"),
        commit_id=__commit_id__,
        tuple_=__version_tuple__,
    )
)


__all__ = ["METADATA"]
