"""
Based on:
https://github.com/microsoft/uf2/blob/7cc2237d58881ee6891dce8a4dde1f89fd2a05ac/utils/uf2conv.py

An entry-point for the 'uf2conv' command.
"""

# built-in
import argparse
import sys
from time import sleep

# third-party
from vcorelib.args import CommandFunction as _CommandFunction

# internal
from yambs import uf2


def error(msg) -> None:
    """Print an error message and exit the program."""
    print(msg, file=sys.stderr)
    sys.exit(1)


# pylint: disable=too-many-statements,too-many-locals,too-many-branches
def uf2conv_cmd(args: argparse.Namespace) -> int:
    """Execute the uf2conv command."""

    uf2.APPSTARTADDR = int(args.base, 0)

    families = uf2.load_families()

    if args.family.upper() in families:
        uf2.FAMILYID = families[args.family.upper()]
    else:
        try:
            uf2.FAMILYID = int(args.family, 0)
        except ValueError:
            msg = "Family ID needs to be a number or one of: "
            error(msg + ", ".join(families.keys()))

    if args.list:
        uf2.list_drives()
    else:
        if not args.input:
            error("Need input file")
        with open(args.input, mode="rb") as path_fd:
            inpbuf = path_fd.read()

        from_uf2 = uf2.is_uf2(inpbuf)
        ext = "uf2"
        if args.deploy:  # pragma: nocover
            outbuf = inpbuf
        elif from_uf2 and not args.info:
            outbuf = uf2.convert_from_uf2(inpbuf)
            ext = "bin"
        elif from_uf2 and args.info:
            outbuf = b""
            uf2.convert_from_uf2(inpbuf)
        elif uf2.is_hex(inpbuf):
            outbuf = uf2.convert_from_hex_to_uf2(inpbuf.decode("utf-8"))
        elif args.carray:
            outbuf = uf2.convert_to_carray(inpbuf)
            ext = "h"
        else:
            outbuf = uf2.convert_to_uf2(inpbuf)

        if not args.deploy and not args.info:
            print(
                (
                    f"Converted to {ext}, output size: {len(outbuf)}, "
                    f"start address: 0x{uf2.APPSTARTADDR:x}"
                )
            )
        if args.convert or ext != "uf2":
            if args.output is None:  # pragma: nocover
                args.output = "flash." + ext

        if args.output:
            uf2.write_file(args.output, outbuf)

        # Deploy the file (if specified).
        if ext == "uf2" and args.deploy:  # pragma: nocover
            drives = uf2.get_drives()
            if len(drives) == 0:
                if args.wait:
                    print("Waiting for drive to deploy...")
                    while len(drives) == 0:
                        sleep(0.1)
                        drives = uf2.get_drives()
                elif not args.output:
                    error("No drive to deploy.")
            for drive in drives:
                print(f"Flashing {drive} ({uf2.board_id(drive)})")
                uf2.write_file(drive + "/NEW.UF2", outbuf)

    return 0


def add_uf2conv_cmd(parser: argparse.ArgumentParser) -> _CommandFunction:
    """Add uf2conv-command arguments to its parser."""

    parser.add_argument(
        "input",
        metavar="INPUT",
        type=str,
        nargs="?",
        help="input file (HEX, BIN or UF2)",
    )
    parser.add_argument(
        "-b",
        "--base",
        dest="base",
        type=str,
        default="0x2000",
        help=(
            "set base address of application "
            "for BIN format (default: 0x2000)"
        ),
    )
    parser.add_argument(
        "-f",
        "--family",
        dest="family",
        type=str,
        default="0x0",
        help="specify familyID - number or name (default: 0x0)",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        dest="output",
        type=str,
        help=(
            'write output to named file; defaults to "flash.uf2"'
            ' or "flash.bin" where sensible'
        ),
    )
    parser.add_argument(
        "-d",
        "--device",
        dest="device_path",
        help="select a device path to flash",
    )
    parser.add_argument(
        "-l", "--list", action="store_true", help="list connected devices"
    )
    parser.add_argument(
        "-c",
        "--convert",
        action="store_true",
        help="do not flash, just convert",
    )
    parser.add_argument(
        "-D",
        "--deploy",
        action="store_true",
        help="just flash, do not convert",
    )
    parser.add_argument(
        "-w", "--wait", action="store_true", help="wait for device to flash"
    )
    parser.add_argument(
        "-C",
        "--carray",
        action="store_true",
        help="convert binary file to a C array, not UF2",
    )
    parser.add_argument(
        "-i",
        "--info",
        action="store_true",
        help="display header information from UF2, do not convert",
    )

    return uf2conv_cmd
