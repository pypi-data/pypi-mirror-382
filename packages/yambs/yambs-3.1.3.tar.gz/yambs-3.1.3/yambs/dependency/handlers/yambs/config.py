"""
A module for working with yambs-project configurations.
"""

# built-in
from pathlib import Path
from typing import Optional, Tuple

# third-party
from vcorelib.paths import Pathlike, normalize

# internal
from yambs.config.common import DEFAULT_CONFIG
from yambs.config.native import Native, load_native
from yambs.dependency.config import DependencyData
from yambs.dependency.handlers.types import DependencyTask


def get_config_path(
    root: Path, config_path: Pathlike = DEFAULT_CONFIG
) -> Path:
    """Obtain the path to a dependency's configuration file."""

    config_path = normalize(config_path)
    path = config_path
    if not path.is_absolute():
        path = root.joinpath(path)

    assert path.is_file(), path

    return path


def handle_config_load(
    task: DependencyTask, directory: Path
) -> Tuple[Optional[Native], Path]:
    """
    Handle initial loading of the dependency's configuration if necessary.
    """

    # Load the project configuration if necessary.
    config = None
    if "slug" not in task.data:
        config = load_native(path=get_config_path(directory), root=directory)
        task.data["slug"] = str(config.project)
        task.data["name"] = config.project.name

    symlink = task.root.joinpath(task.data["name"])
    if not symlink.is_symlink():
        # If the directory is provided as a relative path, treat it as a path
        # relative to the project root and resolve it into something more
        # useful. This doesn't apply to downloaded releases.
        directory = (
            directory
            if directory.is_absolute()
            else task.project_root.joinpath(directory)
        )
        symlink.symlink_to(directory)

    return config, directory


def audit_config_load(
    root: Path,
    include: Path,
    static: Path,
    data: DependencyData,
    config_path: Pathlike = DEFAULT_CONFIG,
    config: Native = None,
) -> DependencyData:
    """
    Load a dependency's configuration data (from disk if necessary) and
    return the result.
    """

    if "dependencies" not in data:
        get_config_path(root, config_path=config_path)

        if config is None:
            config = load_native(
                path=get_config_path(root, config_path=config_path), root=root
            )

        # Ensure some directory linkages are set up ('static' and 'include').
        config.third_party_root.mkdir(parents=True, exist_ok=True)

        for source in [include, static]:
            dest = config.third_party_root.joinpath(source.name)
            if not dest.is_symlink() and not dest.exists():
                dest.symlink_to(source)

        # It's not necessary to keep track of the entire configuration.
        data["dependencies"] = [x.asdict() for x in config.dependencies]

    return data
