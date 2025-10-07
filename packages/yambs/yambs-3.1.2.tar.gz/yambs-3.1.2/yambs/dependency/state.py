"""
A module implementing interfaces for working with dependency states.
"""

# built-in
from enum import StrEnum, auto


class DependencyState(StrEnum):
    """States that a dependency can be in."""

    INIT = auto()
