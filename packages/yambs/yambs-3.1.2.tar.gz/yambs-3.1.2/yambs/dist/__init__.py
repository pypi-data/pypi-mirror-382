"""
A module implementing interfaces for facilitating project distribution.
"""

# built-in
from pathlib import Path
from shutil import copy2, copytree, make_archive
from typing import Any, Dict

# third-party
from vcorelib.paths import rel
from vcorelib.paths.context import in_dir

# internal
from yambs import VERSION
from yambs.config.common import CommonConfig

ARCHIVES = [
    ("tar.gz", "gztar"),
    ("tar.xz", "xztar"),
    ("zip", "zip"),
]


def make_archives(tmp: Path, config: CommonConfig) -> None:
    """Create a distribution that only contains sources."""

    slug = str(config.project)

    for ext, kind in ARCHIVES:
        out = tmp.joinpath(f"{slug}.{ext}")
        out.unlink(missing_ok=True)

        with in_dir(tmp):
            make_archive(slug, kind)

        assert out.is_file(), out

        final = config.dist_root.joinpath(out.name)
        copy2(out, final.resolve())
        out.unlink()

        print(f"Created '{final}'.")


def copy_source_tree(config: CommonConfig, dest: Path) -> None:
    """
    Copy necessary parts of the project source tree to some destination
    directory.
    """

    root = config.root

    for item in [
        x
        for x in [
            config.src_root,
            config.ninja_root,
            root.joinpath("build.ninja"),
            config.file,
        ]
        + [root.joinpath(x) for x in config.data.get("extra_dist", [])]
        if x and x.exists()
    ]:
        relpath = rel(item, base=root)

        curr_dest = dest.joinpath(relpath)
        curr_dest.parent.mkdir(parents=True, exist_ok=True)

        if item.is_dir():
            copytree(item, curr_dest)
        else:
            copy2(item, curr_dest)


def dist_metadata() -> Dict[str, Any]:
    """Get metadata for packaged distributions."""
    return {"yambs_version": VERSION}
