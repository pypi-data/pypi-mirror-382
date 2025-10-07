"""
An entry-point for the 'dist' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace
from pathlib import Path
from shutil import copytree, rmtree
from tempfile import TemporaryDirectory

# third-party
from vcorelib.args import CommandFunction as _CommandFunction
from vcorelib.io import ARBITER
from vcorelib.paths import create_hex_digest

# internal
from yambs.commands.common import add_config_arg
from yambs.config.common import CommonConfig
from yambs.dependency.manager import write_third_party_script
from yambs.dist import copy_source_tree, dist_metadata, make_archives


def dist_cmd(args: _Namespace) -> int:
    """Execute the dist command."""

    config = CommonConfig.load(path=args.config, root=args.dir)

    # Ensure that the third-party build script doesn't contain any instructions
    # to build third-party dependencies (that won't be present for linking).
    write_third_party_script(config.third_party_script)

    # Prepare a temporary directory with project sources.
    with TemporaryDirectory() as tmp:
        path = Path(tmp)

        # Put everything under a directory named after the project slug (name
        # and version).
        base = path.joinpath(str(config.project))

        if args.sources:
            copytree(config.src_root, base)
        else:
            base.mkdir()
            copy_source_tree(config, base)

        # Add JSON metadata.
        ARBITER.encode(base.joinpath("dist.json"), dist_metadata())

        # Remove and re-create the dist directory.
        dist = config.dist_root
        rmtree(dist, ignore_errors=True)
        dist.mkdir()

        make_archives(path, config)

    # Produce a hex digest.
    print(f"Wrote '{create_hex_digest(dist, str(config.project))}'.")

    return 0


def add_dist_cmd(parser: _ArgumentParser) -> _CommandFunction:
    """Add dist-command arguments to its parser."""

    add_config_arg(parser)
    parser.add_argument(
        "-s",
        "--sources",
        action="store_true",
        help="set this flag to only capture source files",
    )
    return dist_cmd
