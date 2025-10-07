"""
A module with interfaces for aggregating sources.
"""

# built-in
from collections import defaultdict
from pathlib import Path
from typing import Dict, Set

# internal
from yambs.generate.common import APP_ROOT

BySuffixPaths = Dict[str, Set[Path]]


def collect_files(
    root: Path, recurse: bool = True, files: BySuffixPaths = None
) -> BySuffixPaths:
    """Collect files (by suffix) from a starting directory."""

    if files is None:
        files = defaultdict(set)

    for item in root.iterdir():
        if item.is_dir() and recurse:
            for suffix, found in collect_files(item, recurse=recurse).items():
                files[suffix].update(found)
        else:
            files[item.suffix].add(item)

    return files


def compile_sources(paths: BySuffixPaths) -> Set[Path]:
    """Get all sources that require compilation."""
    return paths[".c"] | paths[".cc"] | paths[".S"] | paths[".cpp"]


def headers(paths: BySuffixPaths) -> Set[Path]:
    """Get header files."""
    return paths[".h"] | paths[".hpp"] | paths[".hh"]


def sources_headers(paths: BySuffixPaths) -> Set[Path]:
    """Get sources and header files."""
    return compile_sources(paths) | headers(paths)


def populate_sources(
    paths: BySuffixPaths,
    src_root: Path,
    apps: Set[Path],
    regular: Set[Path],
    third_party: Set[Path],
) -> None:
    """Populate application and regular sources from a group of paths."""

    for source in compile_sources(paths):
        try:
            if str(source.relative_to(src_root)).startswith(APP_ROOT):
                apps.add(source)
            else:
                regular.add(source)

        # Handle a source file outside of the main source tree.
        except ValueError:
            third_party.add(source)
