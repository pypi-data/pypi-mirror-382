"""
Integration tests for `UFAClient` upload and download.

These tests read the access token from `~/.deeporigin/api_tokens` (JSON) and use
org_key `deeporigin` and base URL `https://api.edge.deeporigin.io/files/`.
They upload files from `tests/fixtures/` to the remote prefix `tests/ufa/` and
then download them back to validate integrity.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Iterable

import pytest

from ufa.client import UFAClient

FIXTURES_DIR = Path("tests/fixtures")
REMOTE_PREFIX = "tests/ufa/"
ORG_KEY = "deeporigin"
BASE_URL = "https://api.edge.deeporigin.io/files/"


def _read_access_token() -> str:
    """Return the `access` token from `~/.deeporigin/api_tokens`.

    Returns
    -------
    str
        The bearer token to use for authentication.
    """
    token_path = Path.home() / ".deeporigin" / "api_tokens"
    data = json.loads(token_path.read_text())
    return data["access"]


def _iter_fixture_files() -> list[Path]:
    """Return a list of regular files in `tests/fixtures`, excluding dotfiles."""
    if not FIXTURES_DIR.exists():
        return []
    return [
        p
        for p in sorted(FIXTURES_DIR.iterdir())
        if p.is_file() and not p.name.startswith(".")
    ]


@pytest.fixture(scope="session")
def ufa_client() -> UFAClient:
    """Create a `UFAClient` from the local credential file, or skip if missing."""
    try:
        token = _read_access_token()
    except (FileNotFoundError, KeyError):
        pytest.skip(
            "Missing ~/.deeporigin/api_tokens with an 'access' field; skipping integration tests",
        )
    return UFAClient(base_url=BASE_URL, token=token, org_key=ORG_KEY)


def _remote_path_for(local_path: Path) -> str:
    """Return the remote path for a given local fixture file."""
    return f"{REMOTE_PREFIX}{local_path.name}"


@pytest.mark.parametrize(
    "local_path",
    _iter_fixture_files(),
    ids=lambda p: p.name if isinstance(p, Path) else str(p),
)
def test_upload_file(local_path: Path, ufa_client: UFAClient) -> None:
    """Upload each fixture file individually and assert the call succeeds."""
    if not local_path.exists():
        pytest.skip("fixture file missing")
    remote_path = _remote_path_for(local_path)
    asyncio.run(
        ufa_client.upload_file(
            local_file_path=str(local_path),
            org_key=ORG_KEY,
            remote_file_path=remote_path,
        )
    )


@pytest.mark.parametrize(
    "local_path",
    _iter_fixture_files(),
    ids=lambda p: p.name if isinstance(p, Path) else str(p),
)
def test_download_file(tmp_path: Path, local_path: Path, ufa_client: UFAClient) -> None:
    """Upload and then download each fixture file; verify byte-for-byte equality."""
    if not local_path.exists():
        pytest.skip("fixture file missing")
    remote_path = _remote_path_for(local_path)

    # Ensure the file exists remotely for this parameter case
    asyncio.run(
        ufa_client.upload_file(
            local_file_path=str(local_path),
            org_key=ORG_KEY,
            remote_file_path=remote_path,
        )
    )

    # Read original bytes before changing cwd to tmp_path
    original_bytes = Path(local_path).read_bytes()

    # Change working directory so downloads land in `tmp_path`.
    cwd_before = Path.cwd()
    os.chdir(tmp_path)
    try:
        downloaded_path_str = asyncio.run(
            ufa_client.download_file(file_path=remote_path, org_key=ORG_KEY)
        )
        downloaded_path = Path(downloaded_path_str)
        assert downloaded_path.exists()
        assert downloaded_path.name == Path(remote_path).name
        assert downloaded_path.read_bytes() == original_bytes
    finally:
        os.chdir(cwd_before)
