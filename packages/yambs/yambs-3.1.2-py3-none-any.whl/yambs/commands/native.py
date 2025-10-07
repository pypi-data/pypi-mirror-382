"""
An entry-point for the 'native' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace

# third-party
from vcorelib.args import CommandFunction as _CommandFunction

# internal
from yambs.commands.common import (
    add_common_args,
    handle_build,
    log_package,
    run_watch,
)
from yambs.config.native import load_native
from yambs.environment.native import NativeBuildEnvironment


def native_cmd(args: _Namespace) -> int:
    """Execute the native command."""

    log_package()

    config = load_native(path=args.config, root=args.dir)

    NativeBuildEnvironment(config).generate(sources_only=args.sources)
    handle_build(args)

    return run_watch(args, config.src_root, "native")


def add_native_cmd(parser: _ArgumentParser) -> _CommandFunction:
    """Add native-command arguments to its parser."""

    add_common_args(parser)
    return native_cmd
