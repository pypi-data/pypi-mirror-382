"""
An entry-point for the 'compile_config' command.
"""

# built-in
from argparse import ArgumentParser as _ArgumentParser
from argparse import Namespace as _Namespace
from pathlib import Path

# third-party
from vcorelib.args import CommandFunction as _CommandFunction
from vcorelib.dict import MergeStrategy, merge_dicts
from vcorelib.io import ARBITER, DEFAULT_INCLUDES_KEY, encode_if_different

# internal
from yambs.paths import write_dependency_file


def compile_config_cmd(args: _Namespace) -> int:
    """Execute the compile_config command."""

    merge_strat = MergeStrategy.RECURSIVE
    if args.update:
        merge_strat = MergeStrategy.UPDATE

    files_loaded: list[Path] = []

    decode_kwargs = {
        "includes_key": args.includes_key,
        "expect_overwrite": args.expect_overwrite,
        "strategy": merge_strat,
    }

    data = merge_dicts(
        [
            ARBITER.decode(
                file,
                require_success=True,
                files_loaded=files_loaded,
                **decode_kwargs,
            ).data
            for file in args.inputs
        ],
        expect_overwrite=args.expect_overwrite,
        strategy=merge_strat,
    )

    write_dependency_file(args.output, files_loaded, base=args.dir)

    return 0 if encode_if_different(args.output, data, **decode_kwargs) else 1


def add_compile_config_cmd(parser: _ArgumentParser) -> _CommandFunction:
    """Add dist-command arguments to its parser."""

    parser.add_argument(
        "-i",
        "--includes-key",
        default=DEFAULT_INCLUDES_KEY,
        help="top-level key to use for included files (default: %(default)s)",
    )

    parser.add_argument(
        "-u",
        "--update",
        action="store_true",
        help=(
            "whether or not to use the 'update' merge strategy "
            "(instead of 'recursive')"
        ),
    )

    parser.add_argument(
        "-e",
        "--expect-overwrite",
        action="store_true",
        help="allow configuration files to overwrite data when loaded",
    )

    parser.add_argument("output", type=Path, help="file to write")
    parser.add_argument("inputs", nargs="+", type=Path, help="files to read")

    return compile_config_cmd
