"""
A module implementing interfaces for USB Flashing Format (UF2).

See https://github.com/microsoft/uf2.
"""

# built-in
from contextlib import suppress
import os
import os.path
import re
import struct
import subprocess
import sys
from typing import Any, Dict, List, Optional

# third-party
from vcorelib.io import ARBITER
from vcorelib.paths import resource

# internal
from yambs import PKG_NAME

UF2_MAGIC_START0 = 0x0A324655  # "UF2\n"
UF2_MAGIC_START1 = 0x9E5D5157  # Randomly selected
UF2_MAGIC_END = 0x0AB16F30  # Ditto

INFO_FILE = "/INFO_UF2.TXT"

APPSTARTADDR: Optional[int] = 0x2000
FAMILYID = 0x0


def is_uf2(buf: bytes) -> bool:
    """Checks whether or not the provided buffer has the header magic bytes."""

    header = struct.unpack("<II", buf[0:8])
    return bool(header[0] == UF2_MAGIC_START0) and bool(
        header[1] == UF2_MAGIC_START1
    )


def is_hex(buf: bytes) -> bool:
    """
    Determine if the provided buffer has a header that indicates it's Intel
    HEX format.
    """

    result = False

    with suppress(UnicodeDecodeError):
        header = buf[0:30].decode("utf-8")
        result = header[0] == ":" and bool(
            re.match(b"^[:0-9a-fA-F\r\n]+$", buf)
        )

    return result


def convert_to_carray(file_content: bytes) -> bytes:
    """
    Create a C snippet that declares an array equivalent to raw file data.
    """

    outp = f"const unsigned long bindata_len = {len(file_content)};\n"
    outp += "const unsigned char bindata[] __attribute__((aligned(16))) = {"
    for idx, data in enumerate(file_content):
        if idx % 16 == 0:
            outp += "\n"
        outp += f"0x{data:02x}, "
    outp += "\n};\n"

    return bytes(outp, "utf-8")


def convert_to_uf2(file_content: bytes) -> bytes:
    """Convert a file to uf2."""

    assert APPSTARTADDR is not None

    datapadding = b""
    while len(datapadding) < 512 - 256 - 32 - 4:
        datapadding += b"\x00\x00\x00\x00"
    numblocks = (len(file_content) + 255) // 256
    outp = []
    for blockno in range(numblocks):
        ptr = 256 * blockno
        chunk = file_content[ptr : ptr + 256]
        flags = 0x0
        if FAMILYID:
            flags |= 0x2000

        header = struct.pack(
            b"<IIIIIIII",
            UF2_MAGIC_START0,
            UF2_MAGIC_START1,
            flags,
            ptr + APPSTARTADDR,
            256,
            blockno,
            numblocks,
            FAMILYID,
        )
        while len(chunk) < 256:
            chunk += b"\x00"
        block = (
            header + chunk + datapadding + struct.pack(b"<I", UF2_MAGIC_END)
        )
        assert len(block) == 512
        outp.append(block)
    return b"".join(outp)


class Block:
    """A UF2 block."""

    def __init__(self, addr) -> None:
        """Initialize this instance."""

        self.addr = addr
        self.bytes = bytearray(256)

    def encode(self, blockno: int, numblocks: int) -> bytes:
        """Encode a block."""

        flags = 0x0
        if FAMILYID:
            flags |= 0x2000

        header = struct.pack(
            "<IIIIIIII",
            UF2_MAGIC_START0,
            UF2_MAGIC_START1,
            flags,
            self.addr,
            256,
            blockno,
            numblocks,
            FAMILYID,
        )
        header += self.bytes[0:256]
        while len(header) < 512 - 4:
            header += b"\x00"
        header += struct.pack("<I", UF2_MAGIC_END)
        return header


def convert_from_hex_to_uf2(buf: str) -> bytes:
    """Create uf2 bytes from hex data."""

    global APPSTARTADDR  # pylint: disable=global-statement
    APPSTARTADDR = None

    upper = 0
    currblock = None
    blocks = []
    for line in buf.split("\n"):
        if line[0] != ":":  # pragma: nocover
            continue

        i = 1
        rec = []
        while i < len(line) - 1:
            rec.append(int(line[i : i + 2], 16))
            i += 2

        tp_val = rec[3]
        if tp_val == 4:
            upper = ((rec[4] << 8) | rec[5]) << 16
        elif tp_val == 2:  # pragma: nocover
            upper = ((rec[4] << 8) | rec[5]) << 4
        elif tp_val == 1:
            break
        elif tp_val == 0:
            addr = upper + ((rec[1] << 8) | rec[2])
            if APPSTARTADDR is None:
                APPSTARTADDR = addr
            i = 4
            while i < len(rec) - 1:
                if not currblock or currblock.addr & ~0xFF != addr & ~0xFF:
                    currblock = Block(addr & ~0xFF)
                    blocks.append(currblock)
                currblock.bytes[addr & 0xFF] = rec[i]
                addr += 1
                i += 1
    numblocks = len(blocks)
    resfile = b""
    for i in range(0, numblocks):
        resfile += blocks[i].encode(i, numblocks)
    return resfile


def to_str(data: bytes) -> str:
    """Convert bytes to a string."""
    return data.decode("utf-8")


def get_drives(info_file: str = INFO_FILE) -> List[str]:
    """Get mountable drives."""

    drives = []
    if sys.platform == "win32":  # pragma: nocover
        r = subprocess.check_output(
            [
                "powershell",
                "-Command",
                "(Get-WmiObject Win32_LogicalDisk "
                "-Filter \"VolumeName='RPI-RP2'\").DeviceID",
            ]
        )
        drive = to_str(r).strip()
        if drive:
            drives.append(drive)
    else:
        rootpath = "/media"
        if sys.platform == "darwin":  # pragma: nocover
            rootpath = "/Volumes"
        elif sys.platform == "linux":
            tmp = rootpath + "/" + os.environ["USER"]
            if os.path.isdir(tmp):  # pragma: nocover
                rootpath = tmp
        for directory in os.listdir(rootpath):  # pragma: nocover
            drives.append(os.path.join(rootpath, directory))

    return list(filter(lambda x: os.path.isfile(x + info_file), drives))


def board_id(path, info_file: str = INFO_FILE) -> Optional[str]:
    """Get the board identifier."""

    with open(path + info_file, mode="r", encoding="utf-8") as file:
        file_content = file.read()

    match = re.search("Board-ID: ([^\r\n]*)", file_content)
    if match is not None:
        return match.group(1)

    return None


def list_drives() -> None:
    """Print drives."""

    for drive in get_drives():  # pragma: nocover
        print(drive, board_id(drive))


def write_file(name: str, buf: bytes) -> None:
    """Write the given buffer to a file with the given name."""

    with open(name, "wb") as path_fd:
        path_fd.write(buf)
    print(f"Wrote {len(buf)} bytes to {name}")


def load_families() -> Dict[str, int]:
    """
    The expectation is that the `uf2families.json` file is in the same
    directory as this script. Make a path that works using `__file__`
    which contains the full path to this script.
    """

    raw_families = ARBITER.decode(
        resource("uf2families.json", package=PKG_NAME), require_success=True
    ).data

    families = {}
    for family in raw_families:
        families[family["short_name"]] = int(family["id"], 0)  # type: ignore

    return families


# pylint: disable=too-many-statements,too-many-locals,too-many-branches
def convert_from_uf2(
    buf: bytes,
) -> bytes:
    """Convert a uf2-formatted file into a regular one."""

    global APPSTARTADDR  # pylint: disable=global-statement

    numblocks = len(buf) // 512
    curraddr = None
    currfamilyid = None
    families_found: Dict[Any, Any] = {}
    prev_flag = None
    all_flags_same = True
    outp: List[Any] = []

    for blockno in range(numblocks):
        ptr = blockno * 512
        block = buf[ptr : ptr + 512]
        header = struct.unpack(b"<IIIIIIII", block[0:32])

        if (
            header[0] != UF2_MAGIC_START0 or header[1] != UF2_MAGIC_START1
        ):  # pragma: nocover
            print(f"Skipping block at {ptr}; bad magic")
            continue
        if header[2] & 1:  # pragma: nocover
            # NO-flash flag set; skip block
            continue

        datalen = header[4]
        if datalen > 476:  # pragma: nocover
            assert False, f"Invalid UF2 data size at {ptr}"
        newaddr = header[3]

        if (header[2] & 0x2000) and (currfamilyid is None):
            currfamilyid = header[7]

        if curraddr is None or (
            (header[2] & 0x2000) and header[7] != currfamilyid
        ):
            currfamilyid = header[7]
            curraddr = newaddr
            if FAMILYID in [0x0, header[7]]:
                APPSTARTADDR = newaddr

        padding = newaddr - curraddr

        checks = [
            (padding < 0, f"Block out of order at {ptr}"),
            (
                padding > 10 * 1024 * 1024,
                f"More than 10M of padding needed at {ptr}",
            ),
            (padding % 4 != 0, f"Non-word padding size at {ptr}"),
        ]
        for check, msg in checks:
            assert not check, msg

        while padding > 0:  # pragma: nocover
            padding -= 4
            outp += b"\x00\x00\x00\x00"

        if FAMILYID == 0x0 or ((header[2] & 0x2000) and FAMILYID == header[7]):
            outp.append(block[32 : 32 + datalen])

        curraddr = newaddr + datalen
        if header[2] & 0x2000:
            if header[7] in families_found:
                if families_found[header[7]] > newaddr:  # pragma: nocover
                    families_found[header[7]] = newaddr
            else:
                families_found[header[7]] = newaddr

        if prev_flag is None:
            prev_flag = header[2]
        if prev_flag != header[2]:  # pragma: nocover
            all_flags_same = False

        if blockno == (numblocks - 1):
            print("--- UF2 File Header Info ---")

            families = load_families()
            for family_hex, data in families_found.items():
                family_short_name = ""
                for name, value in families.items():
                    if value == family_hex:
                        family_short_name = name
                print(
                    (
                        f"Family ID is {family_short_name:s}, "
                        f"hex value is 0x{family_hex:08x}"
                    )
                )
                print(f"Target Address is 0x{data:08x}")
            if all_flags_same:
                print(f"All block flag values consistent, 0x{header[2]:04x}")
            else:  # pragma: nocover
                print("Flags were not all the same")
            print("----------------------------")
            if len(families_found) > 1 and FAMILYID == 0x0:  # pragma: nocover
                outp = []
                APPSTARTADDR = 0x0

    return b"".join(outp)
