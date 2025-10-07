"""
A module containing common generation utilities.
"""

# built-in
from os import linesep
from pathlib import Path
from typing import Any, Dict

# third-party
from datazen.templates import environment
from jinja2 import Environment, FileSystemLoader
from vcorelib.paths import resource
from vcorelib.paths.context import text_stream_if_different

# internal
from yambs import PKG_NAME

APP_ROOT = "apps"


def get_jinja() -> Environment:
    """Get a jinja environment for package templates."""

    templates_dir = resource("templates", package=PKG_NAME)
    assert templates_dir is not None

    return environment(
        loader=FileSystemLoader([templates_dir], followlinks=True)
    )


def render_template(
    jinja: Environment,
    root: Path,
    name: str,
    data: Dict[str, Any],
    out: str = None,
) -> None:
    """Render a single template."""

    if out is None:
        out = name

    with text_stream_if_different(root.joinpath(out)) as path_fd:
        path_fd.write(jinja.get_template(f"{name}.j2").render(data))
        path_fd.write(linesep)
