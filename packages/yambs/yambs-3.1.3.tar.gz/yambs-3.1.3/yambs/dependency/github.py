"""
A module implementing GitHub dependency interactions.
"""

# built-in
from pathlib import Path
from re import search
from typing import Any, Callable, Dict, Optional

# third-party
import requests
from vcorelib.io.archive import extractall
from vcorelib.io.types import FileExtension
from vcorelib.logging import LoggerMixin, LoggerType
from vcorelib.math import nano_str

# internal
from yambs.github import DEFAULT_RELEASE, ReleaseData, release_data

AssetFilter = Callable[[dict[str, Any]], Optional[Path]]


def download_file_if_missing(
    uri: str, dest: Path, timeout: float = 10.0, chunk_size: int = 4096
) -> None:
    """Download a file if necessary."""

    if not dest.is_file():
        req = requests.get(uri, timeout=timeout)
        with dest.open("wb") as dest_fd:
            for chunk in req.iter_content(chunk_size=chunk_size):
                dest_fd.write(chunk)


def default_filt(
    output: Path, pattern: str = ".*", mkdir: bool = True
) -> AssetFilter:
    """Create a default release-asset filter method."""

    if mkdir:
        output.mkdir(parents=True, exist_ok=True)

    def filt(asset: dict[str, Any]) -> Optional[Path]:
        """Determine if the release asset should be downloaded."""

        result = None

        name = asset["name"]
        if search(pattern, name) is not None:
            result = output.joinpath(name)

        return result

    return filt


def ensure_extracted(
    path: Path, strict: bool = True, logger: LoggerType = None
) -> None:
    """Ensure that all archive files in a directory are extracted."""

    for item in path.iterdir():
        ext = FileExtension.from_path(item)
        if ext is not None and ext.is_archive() and item.is_file():
            dest = item.parent.joinpath(item.name.replace(f".{ext}", ""))
            if not dest.is_dir():
                if logger is not None:
                    logger.info("Extracting '%s' -> '%s'.", item, dest)

                result = extractall(item, dst=item.parent)
                assert result[0]

                if logger is not None:
                    logger.info(
                        "Extracted '%s' in %s.",
                        dest,
                        nano_str(result[1], is_time=True),
                    )

                assert not strict or dest.is_dir(), dest


class GithubDependency(LoggerMixin):
    """A class for managing GitHub dependencies."""

    def __init__(
        self,
        owner: str,
        repo: str,
        *args,
        version: str = DEFAULT_RELEASE,
        data: ReleaseData = None,
        **kwargs,
    ) -> None:
        """Initialize this instance."""

        super().__init__(logger_name=f"{owner}.{repo}")

        if data is None:
            data = release_data(owner, repo, *args, version=version, **kwargs)
        self.data = data

        self.logger.info(
            "Loaded release '%s' (%s).",
            self.data["name"],
            self.data["html_url"],
        )

        # Collect URLs for release content.
        self.download_urls: Dict[str, str] = {
            item["name"]: item["browser_download_url"]
            for item in self.data["assets"]
        }

    def download_release_assets(
        self, filt: AssetFilter, extract: bool = True, strict: bool = True
    ) -> None:
        """Ensure release assets are downloaded."""

        for asset in self.data["assets"]:
            dest = filt(asset)
            if dest is not None:
                download_file_if_missing(asset["browser_download_url"], dest)

                if extract:
                    ensure_extracted(
                        dest.parent, strict=strict, logger=self.logger
                    )
