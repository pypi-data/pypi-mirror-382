"""
A module for writing formatting-related ninja build rules.
"""

# built-in
from itertools import batched
from os import linesep
from pathlib import Path
from typing import Iterable, TextIO

# third-party
from vcorelib.paths import rel
from vcorelib.paths.context import text_stream_if_different

# internal
from yambs.config.common import CommonConfig
from yambs.generate.ninja import write_continuation


def render_format(
    config: CommonConfig,
    paths: Iterable[Path],
    root: Path = None,
    suffix: str = "",
) -> None:
    """Render the ninja source for formatting files."""

    with text_stream_if_different(
        config.ninja_root.joinpath("format.ninja")
    ) as path_fd:
        write_format_target(path_fd, paths, suffix, root)


def final_format_targets(
    stream: TextIO, by_kind: dict[str, list[str]]
) -> None:
    """Create final, highest-level format targets."""

    for target, deps in by_kind.items():
        if deps:
            stream.write(linesep)

            line = f"build {target}: phony "
            offset = " " * len(line)

            stream.write(line)
            stream.write(deps[0])
            for dep in deps[1:]:  # pragma: nocover
                write_continuation(stream, offset)
                stream.write(dep)

            stream.write(linesep)


def write_format_target(
    stream: TextIO, paths: Iterable[Path], suffix: str, root: Path = None
) -> None:
    """
    Write rules and targets for running clang-format on first-party sources
    and headers.
    """

    cmd = f"clang-format{suffix}"

    # Actually formats sources.
    stream.write("rule clang-format" + linesep)
    stream.write(f"  command = {cmd} -i $in" + linesep + linesep)

    # Just checks formatting.
    stream.write("rule clang-format-check" + linesep)
    stream.write(f"  command = {cmd} -n --Werror $in" + linesep)

    targets = [("format", ""), ("format-check", "-check")]
    by_kind: dict[str, list[str]] = {"format": [], "format-check": []}

    # Write format rules in groups of files to ensure command-line invocations
    # don't get too long.
    for idx, group in enumerate(batched(paths, 64)):
        for kind, sfx in targets:
            stream.write(linesep)
            target = f"format-{idx}{sfx}"
            by_kind[kind].append(target)
            line = f"build {target}: clang-format{sfx} "
            offset = " " * len(line)

            stream.write(line)
            stream.write(
                str(group[0] if root is None else rel(group[0], base=root))
            )

            for source in group[1:]:
                write_continuation(stream, offset)
                stream.write(
                    str(source if root is None else rel(source, base=root))
                )

            stream.write(linesep)

    # Create final target.
    final_format_targets(stream, by_kind)
