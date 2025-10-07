"""
A module implementing a dependency handler for other yambs projects.
"""

# built-in
from pathlib import Path
from sys import executable
from typing import Set

# third-party
from vcorelib.paths import rel

# internal
from yambs import PKG_NAME
from yambs.dependency.config import (
    Dependency,
    DependencyData,
    DependencySource,
)
from yambs.dependency.handlers.types import DependencyTask
from yambs.dependency.handlers.yambs.config import (
    audit_config_load,
    handle_config_load,
)
from yambs.dependency.handlers.yambs.github import (
    audit_downloads,
    audit_extract,
    github_release,
)
from yambs.dependency.state import DependencyState


def check_nested_dependencies(
    config: DependencyData, nested: Set[Dependency]
) -> None:
    """
    Determine if a dependency's configuration specifies additional
    dependencies. Add them to the provided set if so.
    """

    for dep in config.get("dependencies", []):
        nested.add(Dependency.create(dep))


def handle_source(task: DependencyTask) -> Path:
    """
    Determine the directory that a given dependency's sources can be found in.
    """

    directory = None

    if task.dep.source == DependencySource.GITHUB:
        audit_downloads(
            task.root, task.data, github_release(task.dep, task.data)
        )
        directory = audit_extract(task.root, task.data)

    elif task.dep.source == DependencySource.DIRECTORY:
        assert task.dep.directory is not None
        directory = task.dep.directory

    assert directory is not None
    return directory


def handle_static_lib(directory: Path, task: DependencyTask) -> None:
    """Handle the third-party dependency's static library."""

    static_lib = directory.joinpath(
        "build", task.dep.target, f"{task.data['slug']}.a"
    )
    task.data["static_library"] = str(static_lib)

    if not static_lib.is_file():
        cmd = []

        rel_dir_arg = str(rel(directory))

        # Always generate build instructions for directory-sourced dependencies
        # if the desired library isn't already built.
        if task.dep.source == DependencySource.DIRECTORY:
            cmd.extend(
                [
                    executable,
                    "-m",
                    PKG_NAME,
                    "-C",
                    rel_dir_arg,
                    "native",
                    "-n",
                    "&&",
                ]
            )

        # Add a build command if the library still needs to be built.
        cmd.extend(["ninja", "-C", rel_dir_arg, f"{task.dep.target}_lib"])
        task.build_commands.append(cmd)

    # Ensure the final static library is linked within the static directory.
    static_include = task.static.joinpath(f"lib{static_lib.name}")
    if not static_include.is_symlink():
        if task.dep.source == DependencySource.GITHUB:
            static_include.symlink_to(
                Path("..", static_lib.relative_to(task.root))
            )
        else:
            static_include.symlink_to(static_lib)

    # Ensure this dependency's static library gets linked.
    task.link_flags.append(f"-l{task.data['slug']}")


def yambs_handler(task: DependencyTask) -> DependencyState:
    """Handle a yambs dependency."""

    directory = handle_source(task)
    config, directory = handle_config_load(task, directory)

    if not task.dep.as_source:
        handle_static_lib(directory, task)

    # Ensure the 'src' directory is linked within the include directory.
    src_include = task.include.joinpath(task.data["name"])
    if not src_include.is_symlink():
        if task.dep.source == DependencySource.GITHUB:
            src_include.symlink_to(Path("..", task.data["name"], "src"))
        else:
            src_include.symlink_to(directory.joinpath("src"))

    if task.dep.as_source:
        task.source_dirs.add(src_include)
        task.compile_flags.extend(
            ["-iquote", str(rel(src_include, base=task.root.parent))]
        )

    # Check if loading the project configuration data is necessary.
    # Read the project's configuration data to find any nested dependencies.
    check_nested_dependencies(
        audit_config_load(
            directory, task.include, task.static, task.data, config=config
        ),
        task.nested,
    )

    return task.current
