"""
A module for generating board-related files.
"""

# built-in
from logging import getLogger
from os import linesep
from pathlib import Path
from typing import Any, Dict, Set, TextIO

# third-party
from jinja2 import Environment
from vcorelib.paths import rel
from vcorelib.paths.context import text_stream_if_different

# internal
from yambs.config.board import Board
from yambs.environment import BuildEnvironment, SourceSets
from yambs.generate.common import APP_ROOT, render_template
from yambs.generate.ninja import write_link_lines, write_source_line
from yambs.translation import is_header, is_source

LOG = getLogger(__name__)


def add_dir(
    stream: TextIO,
    paths: Set[Path],
    path: Path,
    comment: str,
    base: Path,
    current_sources: Set[Path],
    board: Board,
    board_specific: bool = False,
) -> Set[Path]:
    """Add a directory to set of paths."""

    LOG.debug("%s: checking '%s' for sources.", comment, path)

    headers = set()

    if path.is_dir():
        if comment:
            stream.write(linesep + f"# {comment}." + linesep)

        for item in path.iterdir():
            # Recurse into other directories.
            if item.is_dir():
                add_dir(
                    stream,
                    paths,
                    item,
                    "",
                    base,
                    current_sources,
                    board,
                    board_specific=board_specific,
                )

            translator = is_source(item)
            if translator is not None:
                paths.add(
                    write_source_line(
                        stream,
                        item,
                        base,
                        current_sources,
                        board,
                        translator,
                        board_specific=board_specific,
                    )
                )
            elif is_header(item):
                headers.add(item)

    return headers


def create_paths_dict(root: Path, board: Board) -> Dict[str, Any]:
    """Create paths based on common pathing conventions."""

    chip = board.chip

    return {
        "Common": root.joinpath("common"),
        "Chip": root.joinpath("chips", chip.name),
        "Architecture": root.joinpath(chip.architecture.name),
        "CPU": root.joinpath(chip.cpu),
        "Board": root.joinpath("boards", board.name),
    }


def write_sources(
    stream: TextIO,
    board: Board,
    src_root: Path,
    env: BuildEnvironment,
) -> SourceSets:
    """Write the source-file manifest."""

    # Add regular sources.
    all_srcs: Set[Path] = set()

    # Collect header files while we're doing source discovery, too.
    headers: Set[Path] = set()

    for kind, path in create_paths_dict(src_root, board).items():
        headers.update(
            add_dir(
                stream,
                all_srcs,
                path,
                f"{kind} sources",
                src_root,
                env.global_sources,
                board,
            )
        )

    # Add any extra sources this board specified.
    for extra in board.extra_dirs + env.config.data.get(
        "extra_third_party", []
    ):
        # Don't keep track of external headers.
        add_dir(
            stream,
            all_srcs,
            src_root.joinpath("third-party", extra),
            f"Extra sources ({extra})",
            src_root,
            env.global_sources,
            board,
        )

    # Add application sources.
    app_srcs: Set[Path] = set()
    for kind, path in create_paths_dict(
        src_root.joinpath(APP_ROOT), board
    ).items():
        headers.update(
            add_dir(
                stream,
                app_srcs,
                path,
                f"{kind} application sources",
                src_root,
                env.global_sources,
                board,
                # Avoid having a redundant directory in the path when the
                # source directory is already the board-specific one.
                board_specific="boards" not in str(path),
            )
        )

    # Keep track of all header files.
    env.first_party_headers.update(headers)

    # Populate board sources.
    return env.set_board_sources(board, all_srcs, app_srcs)


def generate(
    jinja: Environment, env: BuildEnvironment, sources_only: bool = False
) -> None:
    """Generate board-related ninja files."""

    for board, raw_data in env.config.boards():
        board_root = env.config.ninja_root.joinpath("boards", board.name)
        board_root.mkdir(parents=True, exist_ok=True)

        if not sources_only:
            render_template(jinja, board_root, "board.ninja", raw_data)

        src_root = rel(env.config.src_root)

        # Perform source-file discovery.
        with text_stream_if_different(
            board_root.joinpath("sources.ninja")
        ) as sources_fd:
            with text_stream_if_different(
                board_root.joinpath("apps.ninja")
            ) as apps_fd:
                write_link_lines(
                    apps_fd,
                    src_root,
                    board,
                    write_sources(sources_fd, board, src_root, env),
                )
