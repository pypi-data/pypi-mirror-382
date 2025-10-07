"""
An entry-point for the 'native_manifest' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace

# third-party
from vcorelib.args import CommandFunction as _CommandFunction

# internal
from yambs.commands.common import add_config_arg
from yambs.config.native import load_native
from yambs.environment.native import NativeBuildEnvironment


def native_manifest_cmd(args: _Namespace) -> int:
    """Execute the native_manifest command."""

    NativeBuildEnvironment(
        load_native(path=args.config, root=args.dir)
    ).populate_sources(True)

    return 0


def add_native_manifest_cmd(parser: _ArgumentParser) -> _CommandFunction:
    """Add native_manifest-command arguments to its parser."""

    add_config_arg(parser)
    return native_manifest_cmd
