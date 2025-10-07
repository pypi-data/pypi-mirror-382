from __future__ import annotations

from argparse import ArgumentParser, Namespace
from contextlib import redirect_stdout
from dataclasses import dataclass
from enum import IntEnum, StrEnum
from importlib.metadata import PackageNotFoundError, version
from io import StringIO
import sys
from typing import Literal, Self

STDERR = sys.stderr
BumpType = Literal["major", "minor", "patch"]


class ExitCode(IntEnum):
    """An enumeration of common exit codes used in shell commands."""

    SUCCESS = 0
    FAILURE = 1


class VerParts(StrEnum):
    """Enumeration for version parts."""

    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"

    @classmethod
    def choices(cls) -> list[str]:
        """Return a list of valid version parts."""
        return [version_part.name.lower() for version_part in cls]

    @classmethod
    def parts(cls) -> int:
        """Return the total number of version parts."""
        return len(cls.choices())


VALID_BUMP_TYPES: list[str] = VerParts.choices()
ALL_PARTS: int = VerParts.parts()


@dataclass
class Version:
    """Model to represent a version string."""

    major: int = 0
    """Major version number."""
    minor: int = 0
    """Minor version number."""
    patch: int = 0
    """Patch version number."""

    def __str__(self) -> str:
        return self.version_string

    @classmethod
    def from_string(cls, version_str: str) -> Self:
        """Create a Version instance from a version string.

        Args:
            version_str: A version string in the format "major.minor.patch".

        Returns:
            A Version instance.

        Raises:
            ValueError: If the version string is not in the correct format.
        """
        try:
            version_str = version_str.replace("-", ".").replace("+", ".")
            parts: list[str] = version_str.split(".")[:ALL_PARTS]  # Ignore any extra parts
            major, minor, patch = parts
            return cls(major=int(major), minor=int(minor), patch=int(patch))
        except ValueError as e:
            raise ValueError(
                f"Invalid version string format: {version_str}. Expected integers for major, minor, and patch."
            ) from e

    def increment(self, attr_name: str) -> None:
        """Increment the specified part of the version."""
        setattr(self, attr_name, getattr(self, attr_name) + 1)

    @property
    def version_string(self) -> str:
        """Return the version as a string in the format "major.minor.patch".

        Returns:
            A string representation of the version.
        """
        return f"{self.major}.{self.minor}.{self.patch}"

    def default(self, part: str) -> None:
        """Clear the specified part of the version.

        Args:
            part: The part of the version to clear.
        """
        if hasattr(self, part):
            setattr(self, part, 0)

    def new_version(self, bump_type: str) -> Version:
        """Return a new version string based on the bump type."""
        bump_part: VerParts = VerParts(bump_type.lower())
        self.increment(bump_part.name.lower())
        for part in VerParts:
            if part.value > bump_part.value:
                self.default(part.name.lower())
        return self

    @classmethod
    def from_meta(cls, package_name: str) -> Self:
        """Create a Version instance from the current package version.

        Returns:
            A Version instance with the current package version.

        Raises:
            PackageNotFoundError: If the package is not found.
        """
        try:
            return cls.from_string(version(package_name))
        except PackageNotFoundError as e:
            raise PackageNotFoundError(f"Package '{package_name}' not found: {e}") from e

    @classmethod
    def from_func(cls, package_name: str) -> Self:
        """Create a Version instance from the current package version.

        Returns:
            A Version instance with the current package version.

        Raises:
            PackageNotFoundError: If the package is not found.
        """
        try:
            current_version = version(package_name)
            return cls.from_string(current_version)
        except PackageNotFoundError as e:
            raise PackageNotFoundError(f"Package '{package_name}' not found: {e}") from e


def _bump_version(version: str, bump_type: BumpType) -> Version:
    """Bump the version based on the specified type, mutating in place since there is no reason not to.

    Args:
        version: The current version string (e.g., "1.2.3").
        bump_type: The type of bump ("major", "minor", or "patch").

    Returns:
        The new version string.

    Raises:
        ValueError: If the version format is invalid or bump_type is unsupported.
    """
    return Version.from_string(version).new_version(bump_type)


def _get_version(package_name: str) -> str:
    """Get the version of the specified package.

    Args:
        package_name: The name of the package to get the version for.

    Returns:
        A Version instance representing the current version of the package.

    Raises:
        PackageNotFoundError: If the package is not found.
    """
    record = StringIO()
    with redirect_stdout(record):
        cli_get_version([package_name])
    return record.getvalue().strip()


def cli_get_version(args: list[str] | None = None) -> ExitCode:
    """Get the version of the current package.

    Returns:
        The version of the package.
    """
    if args is None:
        args = sys.argv[1:]
    parser = ArgumentParser(description="Get the version of the package.")
    parser.add_argument("package_name", nargs="?", type=str, help="Name of the package to get the version for.")
    arguments: Namespace = parser.parse_args(args)
    if not arguments.package_name:
        print("No package name provided. Please specify a package name.")
        return ExitCode.FAILURE
    package_name: str = arguments.package_name
    try:
        current_version: str = version(package_name)
        print(current_version)
    except PackageNotFoundError:
        print(f"Package '{package_name}' not found.")
        return ExitCode.FAILURE
    return ExitCode.SUCCESS


def cli_bump(b_type: BumpType, package_name: str, ver: str) -> ExitCode:
    """Bump the version of the current package."""
    if b_type not in VALID_BUMP_TYPES:
        print(f"Invalid argument '{b_type}'. Use one of: {', '.join(VALID_BUMP_TYPES)}.")
        return ExitCode.FAILURE
    try:
        new_version: Version = _bump_version(version=ver, bump_type=b_type)
        print(str(new_version))
        return ExitCode.SUCCESS
    except ValueError:
        try:
            new_version = Version.from_meta(package_name=package_name).new_version(b_type)
            print(str(new_version))
            return ExitCode.SUCCESS
        except PackageNotFoundError:
            print(f"Package '{package_name}' not found.")
            return ExitCode.FAILURE
    except Exception as e:
        print(f"Unexpected error: {e}")
        return ExitCode.FAILURE
