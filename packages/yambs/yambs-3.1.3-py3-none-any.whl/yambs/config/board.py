"""
A data structure describing a board target.
"""

# internal
from pathlib import Path
from typing import Any, Dict, List, NamedTuple


class Architecture(NamedTuple):
    """An instruction-set architecture."""

    name: str
    toolchain: str
    extra_cflags: List[str]

    @staticmethod
    def from_dict(name: str, data: Dict[str, Any]) -> "Architecture":
        """Get an architecture from dictionary data."""
        return Architecture(name, data["toolchain"], data["extra_cflags"])


class Chip(NamedTuple):
    """A microcontroller integrated circuit."""

    name: str
    architecture: Architecture
    cpu: str
    extra_cflags: List[str]
    jlink: List[str]

    @staticmethod
    def from_dict(
        name: str, data: Dict[str, Any], architectures: Dict[str, Any]
    ) -> "Chip":
        """Get a chip from dictionary data."""

        arch = data["architecture"]

        return Chip(
            name,
            Architecture.from_dict(arch, architectures[arch]),
            data["cpu"],
            data["extra_cflags"],
            data["jlink"],
        )


class Board(NamedTuple):
    """A class representing a board's attributes."""

    name: str
    chip: Chip
    extra_cflags: List[str]
    targets: List[str]
    extra_dirs: List[str]
    apps: Dict[str, Path]

    def __hash__(self) -> int:
        """Get a hashing method for this instance."""
        return hash(self.name)

    @property
    def build(self) -> Path:
        """Get a buld directory based on this board."""
        chip = self.chip
        return Path(
            chip.architecture.toolchain, chip.architecture.name, chip.cpu
        )

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
        architectures: Dict[str, Any],
        chips: Dict[str, Any],
    ) -> "Board":
        """Get a board from dictionary data."""

        chip = data["chip"]

        return Board(
            data["name"],
            Chip.from_dict(chip, chips[chip], architectures),
            data["extra_cflags"],
            data["targets"],
            data["extra_dirs"],
            {},
        )
