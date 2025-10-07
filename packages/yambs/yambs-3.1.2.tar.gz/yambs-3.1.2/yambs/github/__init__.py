"""
A module for working with GitHub releases.
"""

# built-in
import os
from typing import Any, Dict
from urllib.parse import ParseResult

# third-party
import requests
from vcorelib.dict.codec import BasicDictCodec as _BasicDictCodec

# internal
from yambs.schemas import YambsDictCodec as _YambsDictCodec

GIHTUB_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
ReleaseData = Dict[str, Any]


class Github(_YambsDictCodec, _BasicDictCodec):
    """GitHub repository information."""


def github_url(
    netloc_prefix: str = "",
    scheme: str = "https",
    path: str = "",
    params: str = "",
    query: str = "",
    fragment: str = "",
) -> ParseResult:
    """See: https://docs.python.org/3/library/urllib.parse.html."""

    netloc = "github.com"
    if netloc_prefix:
        netloc = f"{netloc_prefix}." + netloc

    return ParseResult(
        scheme=scheme,
        netloc=netloc,
        path=path,
        params=params,
        query=query,
        fragment=fragment,
    )


DEFAULT_RELEASE = "latest"


def repo_release_api_url(
    owner: str, repo: str, version: str = DEFAULT_RELEASE
) -> str:
    """Get a URL string for a repository's latest release."""

    version_str = version if version == DEFAULT_RELEASE else f"tags/{version}"

    return github_url(
        netloc_prefix="api",
        path=f"repos/{owner}/{repo}/releases/{version_str}",
    ).geturl()


def check_api_token() -> None:
    """Check for a GitHub API token set via the environment."""

    if "Authorization" not in GIHTUB_HEADERS:
        if "GITHUB_API_TOKEN" in os.environ:
            GIHTUB_HEADERS["Authorization"] = (
                f"Bearer {os.environ['GITHUB_API_TOKEN']}"
            )


def release_data(
    owner: str,
    repo: str,
    *args,
    version: str = DEFAULT_RELEASE,
    timeout: float = None,
    **kwargs,
) -> ReleaseData:
    """Get latest-release data."""

    check_api_token()

    result: ReleaseData = {}

    # codecov was bugging out.
    tries = kwargs.get("tries", 5)

    while not validate_release(result) and tries:
        result = requests.get(
            repo_release_api_url(owner, repo, version=version),
            *args,
            timeout=timeout,
            headers=GIHTUB_HEADERS,
            **kwargs,
        ).json()
        tries -= 1

    assert validate_release(result), result

    return result


def validate_release(data: ReleaseData) -> bool:
    """Ensure that GitHub release data actually contains data."""

    return all(x in data for x in ["name", "html_url", "assets"])
