"""
An entry-point for the 'gen' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace

# third-party
from vcorelib.args import CommandFunction as _CommandFunction

# internal
from yambs.commands.common import add_common_args, handle_build, run_watch
from yambs.config import Config
from yambs.environment import BuildEnvironment
from yambs.generate import generate


def gen_cmd(args: _Namespace) -> int:
    """Execute the gen command."""

    config = Config.load(path=args.config, root=args.dir)

    generate(BuildEnvironment(config), sources_only=args.sources)
    handle_build(args)

    return run_watch(args, config.src_root, "gen")


def add_gen_cmd(parser: _ArgumentParser) -> _CommandFunction:
    """Add gen-command arguments to its parser."""

    add_common_args(parser)
    return gen_cmd
