"""
A module for generating templated outputs.
"""

# built-in
from typing import Any, Dict

# third-party
from vcorelib.io import ARBITER
from vcorelib.paths import resource

# internal
from yambs import PKG_NAME
from yambs.environment import BuildEnvironment
from yambs.generate.architectures import generate as generate_architectures
from yambs.generate.boards import generate as generate_boards
from yambs.generate.chips import generate as generate_chips
from yambs.generate.common import get_jinja, render_template
from yambs.generate.ninja.format import render_format
from yambs.generate.toolchains import generate as generate_toolchains


def create_board_apps(env: BuildEnvironment) -> None:
    """
    Generate JSON metadata to give other tools a simple lookup to application
    sources (e.g. for loading or deploying).
    """

    board_apps: Dict[str, Any] = {}

    # Ensure that the build root directory is present in the full output paths
    # for built applications.
    for board in env.config.board_data:
        board_apps[board.name] = {
            short: str(env.config.build_root.joinpath(path))
            for short, path in board.apps.items()
        }

    ARBITER.encode(
        env.config.ninja_root.joinpath("board_apps.json"),
        board_apps,
    )


def generate(env: BuildEnvironment, sources_only: bool = False) -> None:
    """Generate ninja files."""

    templates_dir = resource("templates", package=PKG_NAME)
    assert templates_dir is not None

    jinja = get_jinja()

    if not sources_only:
        # Render the top-level configuration. This is the only file that's
        # generated into the root directory.
        render_template(jinja, env.config.root, "build.ninja", env.config.data)

        # Generate all other files.
        for gen in [
            generate_chips,
            generate_toolchains,
            generate_architectures,
        ]:
            gen(jinja, env.config)

        # Render the board manifest and rules file.
        for template in ["all.ninja", "rules.ninja"]:
            render_template(
                jinja, env.config.ninja_root, template, env.config.data
            )

    generate_boards(jinja, env, sources_only=sources_only)

    create_board_apps(env)

    # Create format configuration.
    render_format(env.config, env.first_party_sources_headers())
