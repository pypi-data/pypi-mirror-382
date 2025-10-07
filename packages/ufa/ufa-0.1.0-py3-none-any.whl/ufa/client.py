"""
UFA (Unified File Access) service module
"""

import logging
import mimetypes
import os
from pathlib import Path

import anyio
import httpx

logger = logging.getLogger(__name__)


class UFAClient:
    """Service for interacting with UFA"""

    def __init__(
        self,
        *,
        base_url: str,
        token: str,
        max_retries: int = 3,
        org_key: str,
    ):
        self.base_url = base_url
        if not token:
            raise ValueError("UFAClient requires a non-empty bearer token")
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        self.max_retries = max_retries
        self.org_key = org_key

    async def download_file(self, file_path: str, org_key: str) -> str:
        """
        Fetch file content from UFA service with retry logic

        Parameters
        ----------
        file_path : str
            The UFA file path
        org_key : str
            Organization key for authentication

        Returns
        -------
        str
            Local file path of the downloaded file

        Raises
        ------
        UFADownloadError
            If file cannot be retrieved from UFA after all retry attempts
        """

        clean_path = file_path.lstrip("/")
        filename = os.path.basename(clean_path) or "downloaded_file"
        destination_path = Path.cwd() / filename

        # If the file already exists locally, do not download again
        if destination_path.exists():
            logger.info(f"File already exists at {destination_path}; skipping download")
            return str(destination_path)

        async with httpx.AsyncClient() as client:
            direct_url = f"{self.base_url}/{org_key}/{clean_path}"

            try:
                response = await self._make_request(client, direct_url)
                if response.status_code == 200:
                    with destination_path.open("wb") as f:
                        f.write(response.content)
                    logger.info(f"Saved file via direct download to {destination_path}")
                    return str(destination_path)
            except httpx.HTTPError as e:
                logger.warning(f"Direct download failed for {file_path}: {str(e)}")

            signed_url = f"{self.base_url}/signedUrl/download/{org_key}/{clean_path}"

            try:
                response = await self._make_request(client, signed_url)
                if response.status_code == 200:
                    with destination_path.open("wb") as f:
                        f.write(response.content)
                    logger.info(f"Saved file via signed URL to {destination_path}")
                    return str(destination_path)
            except httpx.HTTPError as e:
                logger.error(f"Signed URL download failed for {file_path}: {str(e)}")
                raise UFADownloadError(
                    f"Failed to retrieve file from UFA after all attempts: {file_path}"
                ) from None

    async def _make_request(
        self, client: httpx.AsyncClient, url: str
    ) -> httpx.Response:
        """Make HTTP request with retry logic"""
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response
            except httpx.HTTPError as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    logger.warning(f"Request attempt {attempt + 1} failed: {str(e)}")
                    continue
                break

        raise last_exception

    async def upload_file(
        self,
        local_file_path: str,
        org_key: str,
        remote_file_path: str,
    ) -> object:
        """
        Upload a single file to UFA using multipart/form-data via HTTP PUT.

        Parameters
        ----------
        local_file_path : str
            Path to the local file on disk to upload.
        org_key : str
            Organization key for authentication and routing.
        remote_file_path : str
            The destination path in UFA (no leading slash required).

        Returns
        -------
        object
            Parsed JSON if the server responds with JSON, otherwise response text.

        Raises
        ------
        FileNotFoundError
            If the local file is missing.
        UFAUploadError
            If the upload fails after all retry attempts.
        """

        if not os.path.isfile(local_file_path):
            raise FileNotFoundError(f"Local file does not exist: {local_file_path}")

        clean_remote_path = remote_file_path.lstrip("/")
        url = f"{self.base_url}/{org_key}/{clean_remote_path}"

        content_type, _ = mimetypes.guess_type(local_file_path)
        if not content_type:
            content_type = "application/octet-stream"

        filename = os.path.basename(local_file_path)

        last_exception: Exception | None = None

        async with httpx.AsyncClient() as client:
            for attempt in range(self.max_retries):
                try:
                    # Read file content asynchronously to avoid blocking the event loop
                    async with await anyio.open_file(local_file_path, "rb") as afp:
                        file_bytes = await afp.read()
                    files = {"file": (filename, file_bytes, content_type)}
                    # Do not set Content-Type header explicitly; httpx will set proper multipart boundary.
                    response = await client.put(url, headers=self.headers, files=files)
                    response.raise_for_status()

                    # Try to return JSON when possible
                    resp_ct = response.headers.get("content-type", "")
                    if "application/json" in resp_ct:
                        return response.json()
                    return response.text
                except httpx.HTTPError as e:
                    last_exception = e
                    if attempt < self.max_retries - 1:
                        logger.warning(f"Upload attempt {attempt + 1} failed: {str(e)}")
                        continue
                    break

        logger.error(
            "Failed to upload file to UFA after all attempts: %s -> %s",
            local_file_path,
            url,
        )
        raise UFAUploadError(
            f"Failed to upload file to UFA after all attempts: {local_file_path} -> {url}"
        ) from last_exception


class UFAError(Exception):
    """Base exception for UFA client errors."""


class UFADownloadError(UFAError):
    """Raised when downloading a file from UFA fails after retries."""


class UFAUploadError(UFAError):
    """Raised when uploading a file to UFA fails after retries."""
