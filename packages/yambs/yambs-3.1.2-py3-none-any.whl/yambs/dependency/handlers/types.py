"""
A module declaring shared types.
"""

# built-in
from pathlib import Path
from typing import Callable, List, NamedTuple, Set

# internal
from yambs.dependency.config import Dependency, DependencyData
from yambs.dependency.state import DependencyState


class DependencyTask(NamedTuple):
    """A container for dependency handler invocation data."""

    # Useful paths.
    root: Path
    project_root: Path
    include: Path
    static: Path

    build_commands: List[List[str]]
    source_dirs: Set[Path]

    compile_flags: List[str]
    link_flags: List[str]

    dep: Dependency
    current: DependencyState
    data: DependencyData

    nested: Set[Dependency]


DependencyHandler = Callable[[DependencyTask], DependencyState]
