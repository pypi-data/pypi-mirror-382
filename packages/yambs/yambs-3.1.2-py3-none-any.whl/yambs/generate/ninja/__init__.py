"""
A module for working with ninja syntax.
"""

# built-in
from os import linesep
from pathlib import Path
from typing import Set, TextIO

# internal
from yambs.config.board import Board
from yambs.environment import SourceSets
from yambs.translation import BUILD_DIR_VAR, SourceTranslator


def write_source_line(
    stream: TextIO,
    source: Path,
    base: Path,
    current_sources: Set[Path],
    board: Board,
    translator: SourceTranslator,
    board_specific: bool = False,
) -> Path:
    """Write a ninja configuration line for a source file."""

    dest = source
    if board_specific:
        dest = source.parent.joinpath(board.name, source.name)

    build_loc = board.build.joinpath(dest)

    # Don't generate any duplicate compilation rules.
    if build_loc not in current_sources:
        current_sources.add(build_loc)

        stream.write(
            (
                f"build {translator.output(dest.relative_to(base))}: "
                f"{translator.rule} $src_dir/{source.relative_to(base)}"
            )
        )

        # Any regular source file depends on all of the boards generated
        # depencencies.
        if not translator.generated_header:
            stream.write(" || ${board}_generated")

        stream.write(linesep)

    return dest


def write_continuation(stream: TextIO, offset: str) -> None:
    """Write a line continuation."""
    stream.write(" $" + linesep + offset)


def write_link_line(
    stream: TextIO, source: Path, base: Path, board: Board, sources: SourceSets
) -> None:
    """
    Write a ninja configuration line for an application requiring linking.
    """

    source = source.relative_to(base)

    by_suffix = {
        x: source.with_suffix(f".{x}")
        for x in ["o", "elf", "bin", "hex", "dump", "uf2"]
    }

    elf = f"{BUILD_DIR_VAR}/{by_suffix['elf']}"
    line = f"build {elf}: link "
    offset = " " * len(line)
    stream.write(line + f"{BUILD_DIR_VAR}/{by_suffix['o']}")

    for src, trans in sources.link_sources():
        write_continuation(stream, offset)
        stream.write(str(trans.output(src.relative_to(base))))
    stream.write(linesep)

    # Add lines for creating binaries.
    stream.write(
        f"build {BUILD_DIR_VAR}/{by_suffix['bin']}: bin {elf}" + linesep
    )

    # Add an objdump target.
    stream.write(
        f"build {BUILD_DIR_VAR}/{by_suffix['dump']}: dump {elf}" + linesep
    )

    # Add an hex target.
    hex_path = f"{BUILD_DIR_VAR}/{by_suffix['hex']}"
    stream.write(f"build {hex_path}: hex {elf}" + linesep)

    # Add a uf2 target.
    stream.write(f"build {BUILD_DIR_VAR}/{by_suffix['uf2']}: uf2 {hex_path}")

    stream.write(linesep + linesep)

    # Add this application to the board's data structure.
    out = by_suffix["elf"].with_suffix("")
    board.apps[str(out)] = board.build.joinpath(out)


def write_generated_phony(
    stream: TextIO, sources: SourceSets, src_root: Path
) -> None:
    """Write generated-file phony target."""

    # Write generated-file phony target.
    stream.write("# A target to generate additional headers." + linesep)
    phony_line = "build ${board}_generated: phony"
    offset = " " * (len(phony_line) + 1)

    stream.write(phony_line)

    implicit = list(sources.implicit_sources())
    if implicit:
        src, trans = implicit[0]
        stream.write(f" {trans.output(src.relative_to(src_root))}")
        for src, trans in implicit[1:]:
            write_continuation(stream, offset)
            stream.write(str(trans.output(src.relative_to(src_root))))
    stream.write(linesep + linesep)


def write_link_lines(
    stream: TextIO, src_root: Path, board: Board, sources: SourceSets
) -> None:
    """Write the application manifest and phony targets."""

    # Write the application manifest.
    for app_src in sources.apps:
        write_link_line(stream, app_src, src_root, board, sources)

    write_generated_phony(stream, sources, src_root)

    # Write the phony target.
    stream.write("# A target to build all applications." + linesep)
    write_phony(stream, sources.apps, src_root, board.name)


def write_phony(
    stream: TextIO, app_srcs: Set[Path], base: Path, board: str
) -> None:
    """Write the phony target."""

    phonies = [
        ("apps", ".bin"),
        ("hexs", ".hex"),
        ("dumps", ".dump"),
        ("uf2s", ".uf2"),
    ]

    if app_srcs:
        for phony, suffix in phonies:
            srcs = list(app_srcs)
            first = srcs[0].relative_to(base)
            srcs = srcs[1:]

            line = f"build {board}_{phony}: phony "
            offset = " " * len(line)
            stream.write(line + f"{BUILD_DIR_VAR}/{first.with_suffix(suffix)}")
            for src in srcs:
                write_continuation(stream, offset)
                src = src.relative_to(base)
                stream.write(f"{BUILD_DIR_VAR}/{src.with_suffix(suffix)}")

            stream.write(linesep)


def write_link(
    stream: TextIO,
    output: Path,
    entry_object: Path,
    outputs: Set[Path],
    wasm: bool = False,
) -> None:
    """Write a 'link' rule."""

    pairs = [(output.suffix, entry_object.suffix, "link")]

    if wasm:
        pairs.append((".html", ".wasm", "link_no_map"))

    for out_suffix, entry_suffx, rule in pairs:
        line = f"build {output.with_suffix(out_suffix)}: {rule} "
        offset = " " * len(line)

        stream.write(line + str(entry_object.with_suffix(entry_suffx)))

        for file in outputs:
            write_continuation(stream, offset)
            stream.write(str(file.with_suffix(entry_suffx)))

        # Executables can't be linked until third-party dependencies are
        # actually built.
        stream.write(" | ${variant}_third_party" + linesep + linesep)


def variant_phony(
    stream: TextIO,
    elfs_list: list[Path],
    uf2_family: str = None,
    wasm: bool = False,
):
    """Write variant-specific phony targets."""

    line = "build ${variant}_apps: phony "
    offset = " " * len(line)

    stream.write(line + str(elfs_list[0]))
    for elf in elfs_list[1:]:
        write_continuation(stream, offset)
        stream.write(str(elf))
    stream.write(linesep)

    suffixes = []
    if wasm:
        suffixes.append("html")
    if uf2_family:
        suffixes.append("uf2")

    for suffix in suffixes:
        line = "build ${variant}_" + f"{suffix}s: phony "
        offset = " " * len(line)

        outputs = [x.with_suffix("." + suffix) for x in elfs_list]

        stream.write(line + str(outputs[0]))
        for elf in outputs[1:]:
            write_continuation(stream, offset)
            stream.write(str(elf))
        stream.write(linesep)
