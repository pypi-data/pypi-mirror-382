"""
A module for aggregating dependency handlers.
"""

# built-in
from typing import Dict

# internal
from yambs.dependency.config import DependencyKind
from yambs.dependency.handlers.types import DependencyHandler
from yambs.dependency.handlers.yambs import yambs_handler

HANDLERS: Dict[DependencyKind, DependencyHandler] = {
    DependencyKind.YAMBS: yambs_handler
}
