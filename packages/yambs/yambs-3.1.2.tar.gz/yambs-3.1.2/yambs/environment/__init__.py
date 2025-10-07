"""
A module implementing a build environment state manager.
"""

# built-in
from pathlib import Path
from typing import Dict, Iterator, NamedTuple, Set, Tuple

# third-party
from vcorelib.logging import LoggerMixin

# internal
from yambs.config import Config
from yambs.config.board import Board
from yambs.translation import SourceTranslator, get_translator, is_source

SourceAndTranslator = Tuple[Path, SourceTranslator]


class SourceSets(NamedTuple):
    """A structure for managing different kinds of source paths."""

    regular: Set[Path]
    apps: Set[Path]

    def sources(self) -> Iterator[SourceAndTranslator]:
        """Iterate over sources and their source translator."""
        for source in self.regular:
            yield source, get_translator(source)

    def link_sources(self) -> Iterator[SourceAndTranslator]:
        """Get all sources that are directly provided to the linker."""

        for source, trans in self.sources():
            if trans.gets_linked:
                yield source, trans

    def implicit_sources(self) -> Iterator[SourceAndTranslator]:
        """Iterate over generated sources."""

        for source, trans in self.sources():
            if trans.generated_header:
                yield source, trans


class BuildEnvironment(LoggerMixin):
    """A class implementing a simple build environment."""

    def __init__(self, config: Config) -> None:
        """Initialize this instance."""

        super().__init__()

        self.config = config

        # Keep track of all overall sources, so that no duplicate rules are
        # generated.
        self.global_sources: Set[Path] = set()
        self.first_party_headers: Set[Path] = set()

        # Keep track of sources by board.
        self.by_board: Dict[Board, SourceSets] = {}

    def first_party_sources_headers(self) -> Iterator[Path]:
        """
        Get all first-party sources and headers. This could be useful for
        formatting or static analysis tooling where third-party sources
        should be excluded.
        """

        visited: Set[Path] = set()

        # We can't use 'global sources' for this because it uses build paths
        # instead of source-tree paths.
        for sources in self.by_board.values():
            for source in sources.regular | sources.apps:
                # Try to remove board-specific namespacing. This still might
                # not point to a real file because some of these sources may
                # be generated.
                if not source.is_file():
                    source = source.parent.parent.joinpath(source.name)

                # Skip generated headers and assembly files.
                translator = is_source(source)
                if (
                    translator is not None and translator.generated_header
                ) or source.suffix == ".S":
                    continue

                # Skip third-party sources.
                if "third-party" not in str(source) and source not in visited:
                    yield source
                    visited.add(source)

        yield from self.first_party_headers

    def set_board_sources(
        self, board: Board, regular: Set[Path], apps: Set[Path]
    ) -> SourceSets:
        """Finalize source sets for a given board."""

        assert board not in self.by_board, board
        sources = SourceSets(regular, apps)
        self.by_board[board] = sources

        self.logger.info(
            "(%s) Found %d sources and %d applications.",
            board.name,
            len(sources.regular),
            len(sources.apps),
        )

        return sources
