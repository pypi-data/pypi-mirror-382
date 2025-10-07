"""
A module for generating architecture-related files.
"""

# third-party
from jinja2 import Environment

# internal
from yambs.config.common import CommonConfig
from yambs.generate.common import render_template


def generate(jinja: Environment, config: CommonConfig) -> None:
    """Generate architecture-related ninja files."""

    for name, data in config.data["architectures"].items():
        architectures_root = config.ninja_root.joinpath("architectures", name)
        architectures_root.mkdir(parents=True, exist_ok=True)

        render_template(
            jinja,
            architectures_root,
            "architecture.ninja",
            data,
        )
