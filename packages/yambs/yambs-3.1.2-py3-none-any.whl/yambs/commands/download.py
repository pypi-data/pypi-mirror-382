"""
An entry-point for the 'download' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace
from pathlib import Path

# third-party
from vcorelib.args import CommandFunction as _CommandFunction

# internal
from yambs.dependency.github import GithubDependency, default_filt

DEFAULT_PATTERN = ".*"


def download_cmd(args: _Namespace) -> int:
    """Execute the download command."""

    dep = GithubDependency(args.owner, args.repo)

    # Download and extract things.
    args.output.mkdir(parents=True, exist_ok=True)
    dep.download_release_assets(
        default_filt(args.output.joinpath(args.repo), pattern=args.pattern),
        strict=args.pattern == DEFAULT_PATTERN,
    )

    return 0


def add_download_cmd(parser: _ArgumentParser) -> _CommandFunction:
    """Add download-command arguments to its parser."""

    parser.add_argument(
        "-o",
        "--owner",
        default="libre-embedded",
        help="repository owner (default: '%(default)s')",
    )
    parser.add_argument(
        "-r",
        "--repo",
        default="toolchains",
        help="repository name (default: '%(default)s')",
    )
    parser.add_argument(
        "-O",
        "--output",
        type=Path,
        default=Path(),
        help="output directory (default: '%(default)s')",
    )
    parser.add_argument(
        "-p",
        "--pattern",
        default=DEFAULT_PATTERN,
        help=(
            "a pattern to use to select project "
            "specifications filtered by name"
        ),
    )

    return download_cmd
