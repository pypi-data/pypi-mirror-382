"""
A module with interfaces for describing how sources are translated into
outputs.
"""

# built-in
from functools import lru_cache
from os import linesep
from pathlib import Path
from typing import NamedTuple, Optional, TextIO

HEADER_EXTENSIONS = {".h", ".hpp"}
BUILD_DIR_VAR = "$build_dir"
BUILD_DIR_PATH = Path(BUILD_DIR_VAR)


class SourceTranslator(NamedTuple):
    """
    A structure for keeping track of how source files become different types
    of output files.
    """

    rule: str = "cc"
    output_extension: str = ".o"
    dest: Path = Path(BUILD_DIR_VAR)

    def translate(self, path: Path) -> Path:
        """Translate a path by changing its suffix."""
        return path.with_suffix(self.output_extension)

    def output(self, path: Path) -> Path:
        """Get the output file from a given path."""
        return self.dest.joinpath(self.translate(path))

    @property
    def gets_linked(self) -> bool:
        """
        Determine if this source's output gets linked into a final image or
        executable.
        """
        return self.output_extension == ".o"

    @property
    def generated_header(self) -> bool:
        """Determine if this translation produces a header file."""
        return self.output_extension in HEADER_EXTENSIONS

    def write(
        self,
        stream: TextIO,
        out: Path,
        source: str,
        rule: str = "build",
        wasm: bool = False,
    ) -> None:
        """Write a ninja rule to the stream."""

        stream.write(f"{rule} {out}: {self.rule} {source}")
        stream.write(linesep)

        # Also add a '.wasm' variant.
        if wasm:
            stream.write(
                (f"build {out.with_suffix('.wasm')}: " f"{self.rule} {source}")
            )
            stream.write(linesep)


DEFAULT = SourceTranslator()


SOURCES = {
    ".c": DEFAULT,
    ".S": DEFAULT,
    ".cc": SourceTranslator(rule="cxx"),
    ".cpp": SourceTranslator(rule="cxx"),
    ".pio": SourceTranslator("pio", ".h", Path("$generated_dir")),
}


@lru_cache(maxsize=None)
def is_source(path: Path) -> Optional[SourceTranslator]:
    """Determine if a file is a source file."""
    return SOURCES.get(path.suffix)


def is_header(path: Path) -> bool:
    """determine if a path points to a header file."""
    return path.suffix in HEADER_EXTENSIONS


def get_translator(path: Path) -> SourceTranslator:
    """Get the source translator for a given source."""

    result = is_source(path)
    assert result is not None
    return result
