from __future__ import annotations

from argparse import Action, ArgumentParser, Namespace
import sys
from typing import Any

from bear_epoch_time._internal._get_version import STDERR, VALID_BUMP_TYPES, BumpType, ExitCode, cli_bump
from bear_epoch_time._internal.debug import METADATA, _get_package_info, _print_debug_info  # type: ignore[import]


class _DebugInfo(Action):
    def __init__(self, nargs: int | str | None = 0, **kwargs: Any) -> None:
        super().__init__(nargs=nargs, **kwargs)

    def __call__(self, *_: Any, **__: Any) -> None:
        _print_debug_info()
        sys.exit(ExitCode.SUCCESS)


class _About(Action):
    def __init__(self, nargs: int | str | None = 0, **kwargs: Any) -> None:
        super().__init__(nargs=nargs, **kwargs)

    def __call__(self, *_: Any, **__: Any) -> None:
        print(_get_package_info())
        sys.exit(ExitCode.SUCCESS)


class _Version(Action):
    def __init__(self, nargs: int | str | None = 0, **kwargs: Any) -> None:
        super().__init__(nargs=nargs, **kwargs)

    def __call__(self, *_: Any, **__: Any) -> None:
        version: str = f"{METADATA.name} v{METADATA.version}"
        print(version)
        sys.exit(ExitCode.SUCCESS)


def get_version() -> ExitCode:
    """CLI command to get the version of the package."""
    print(METADATA.version)
    return ExitCode.SUCCESS


def get_parser(args: list[str]) -> Namespace:
    parser = ArgumentParser(description=METADATA.name.capitalize(), prog=METADATA.name, exit_on_error=False)
    parser.add_argument("-V", "--version", action=_Version, help="Print the version of the package")
    subparser = parser.add_subparsers(dest="command", required=False, help="Available commands")
    subparser.add_parser("version", help="Get the current version of the package")
    bump = subparser.add_parser("bump", help="Bump the version of the package")
    bump.add_argument("bump_type", type=str, choices=VALID_BUMP_TYPES, help="major, minor, or patch")
    parser.add_argument("--about", action=_About, help="Print information about the package")
    parser.add_argument("--debug_info", action=_DebugInfo, help="Print debug information")
    return parser.parse_args(args)


def main(args: list[str] | None = None) -> ExitCode:
    """Main entry point for the CLI.

    This function is called when the CLI is executed. It can be used to
    initialize the CLI, parse arguments, and execute commands.

    Args:
        args (list[str] | None): A list of command-line arguments. If None, uses sys.argv[1:].

    Returns:
        int: Exit code of the CLI execution. 0 for success, non-zero for failure.
    """
    if args is None:
        args = sys.argv[1:]
    try:
        opts: Namespace = get_parser(args)
        command: str | None = opts.command
        if command == "version":
            return get_version()
        if command == "bump":
            if not hasattr(opts, "bump_type"):
                print("Error: 'bump-version' command requires a 'bump_type' argument.", file=STDERR)
                return ExitCode.FAILURE
            bump_type: BumpType = opts.bump_type
            return cli_bump(bump_type, METADATA.name, METADATA.version)
    except Exception as e:
        print(f"Error initializing CLI: {e}", file=STDERR)
        return ExitCode.FAILURE
    return ExitCode.SUCCESS


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
