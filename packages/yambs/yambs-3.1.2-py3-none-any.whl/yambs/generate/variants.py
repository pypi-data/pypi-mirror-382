"""
A module for generating variant-related files.
"""

# built-in
from contextlib import contextmanager
from typing import Any, Dict, Iterator, List

# third-party
from jinja2 import Environment

# internal
from yambs.config.common import CommonConfig
from yambs.generate.common import render_template

FlagGroups = Dict[str, List[str]]


@contextmanager
def modified_variant_data(
    name: str,
    data: Dict[str, Any],
    cflag_groups: FlagGroups,
    ldflag_groups: FlagGroups,
) -> Iterator[None]:
    """
    Ensure that cflag groups are processed, and that the variant has access to
    its name while rendering.
    """

    orig_c = data["extra_cflags"]
    orig_ld = data["extra_ldflags"]

    # Process cflag groups.
    flags = set(orig_c + cflag_groups.get(name, []))
    for group in data["cflag_groups"]:
        flags |= set(cflag_groups[group])
    data["extra_cflags"] = flags

    # Process ldflag groups.
    flags = set(orig_ld + ldflag_groups.get(name, []))
    for group in data["ldflag_groups"]:
        flags |= set(ldflag_groups[group])
    data["extra_ldflags"] = flags

    # Add other useful data.
    data["name"] = name

    yield

    # Restore original data.
    del data["name"]
    data["extra_cflags"] = orig_c
    data["extra_ldflags"] = orig_ld


def generate(
    jinja: Environment,
    config: CommonConfig,
    cflag_groups: FlagGroups,
    ldflag_groups: FlagGroups,
) -> None:
    """Generate variant-related ninja files."""

    for name, data in config.data["variants"].items():
        if data["enabled"]:
            variants_root = config.ninja_root.joinpath("variants", name)
            variants_root.mkdir(parents=True, exist_ok=True)
            with modified_variant_data(
                name, data, cflag_groups, ldflag_groups
            ):
                render_template(
                    jinja,
                    variants_root,
                    "variant.ninja",
                    data,
                )
