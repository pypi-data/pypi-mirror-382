# =====================================
# generator=datazen
# version=3.2.3
# hash=01315de1d4442a08f5ab9bc31f9d58b9
# =====================================

"""
A module aggregating package commands.
"""

# third-party
from vcorelib.args import CommandRegister as _CommandRegister

# internal
from yambs.commands.compile_config import add_compile_config_cmd
from yambs.commands.dist import add_dist_cmd
from yambs.commands.download import add_download_cmd
from yambs.commands.gen import add_gen_cmd
from yambs.commands.native import add_native_cmd
from yambs.commands.native_manifest import add_native_manifest_cmd
from yambs.commands.uf2conv import add_uf2conv_cmd


def commands() -> list[tuple[str, str, _CommandRegister]]:
    """Get this package's commands."""

    return [
        (
            "compile_config",
            "load configuration data and write results to a file",
            add_compile_config_cmd,
        ),
        (
            "dist",
            "create a source distribution",
            add_dist_cmd,
        ),
        (
            "download",
            "download GitHub release assets",
            add_download_cmd,
        ),
        (
            "gen",
            "poll the source tree and generate any new build files",
            add_gen_cmd,
        ),
        (
            "native",
            "generate build files for native-style projects",
            add_native_cmd,
        ),
        (
            "native_manifest",
            "generate a source-file manifest for native-style projects",
            add_native_manifest_cmd,
        ),
        (
            "uf2conv",
            "convert to UF2 or flash directly",
            add_uf2conv_cmd,
        ),
        ("noop", "command stub (does nothing)", lambda _: lambda _: 0),
    ]
