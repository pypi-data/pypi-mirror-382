"""
A module implementing a configuration interface for the package.
"""

# built-in
from typing import Any, Dict, Iterator, List, Tuple

# third-party
from vcorelib.io.types import JsonObject as _JsonObject

# internal
from yambs.config.board import Board
from yambs.config.common import CommonConfig


class Config(CommonConfig):
    """The top-level configuration object for the package."""

    board_data: List[Board]
    boards_by_name: Dict[str, Board]

    def init(self, data: _JsonObject) -> None:
        """Initialize this instance."""

        super().init(data)
        self.boards_by_name = {}
        self._init_boards()

    def _init_boards(self) -> None:
        """Initialize board data."""

        self.board_data = [
            Board.from_dict(x, self.data["architectures"], self.data["chips"])
            for x in self.data["boards"]
        ]
        for board in self.board_data:
            self.boards_by_name[board.name] = board

    def boards(self) -> Iterator[Tuple[Board, Dict[str, Any]]]:
        """Iterate over boards."""

        for inst, board in zip(self.board_data, self.data["boards"]):
            yield inst, board
