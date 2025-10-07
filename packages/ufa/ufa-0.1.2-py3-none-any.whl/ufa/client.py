"""
UFA (Unified File Access) service module
"""

import logging
import mimetypes
import os
from pathlib import Path
from urllib.parse import quote

import anyio
import httpx
from beartype import beartype

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
        # Normalize base_url to avoid accidental double slashes in constructed URLs
        self.base_url = base_url.rstrip("/")
        if not token:
            raise ValueError("UFAClient requires a non-empty bearer token")
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        self.max_retries = max_retries
        self.org_key = org_key

    @beartype
    async def download_file(
        self,
        *,
        remote_file_path: str,
        download_dir: str | Path | None = None,
    ) -> str:
        """
        Fetch file content from UFA service with retry logic

        Parameters
        ----------
        file_path : str
            The UFA file path
        download_dir : str | Path | None
            Directory in which to save the downloaded file. If None, uses the
            current working directory. The directory is created if needed.

        Returns
        -------
        str
            Local file path of the downloaded file

        Raises
        ------
        UFADownloadError
            If file cannot be retrieved from UFA after all retry attempts
        """

        clean_path = remote_file_path.lstrip("/")
        filename = os.path.basename(clean_path) or "downloaded_file"
        target_dir = Path(download_dir) if download_dir is not None else Path.cwd()
        target_dir.mkdir(parents=True, exist_ok=True)
        destination_path = target_dir / filename

        # If the file already exists locally, do not download again
        if destination_path.exists():
            logger.info(f"File already exists at {destination_path}; skipping download")
            return str(destination_path)

        async with httpx.AsyncClient() as client:
            direct_url = f"{self.base_url}/{self.org_key}/{clean_path}"
            logger.debug(
                "Attempting direct download: url=%s dest=%s",
                direct_url,
                destination_path,
            )

            try:
                response = await self._make_request(client, direct_url)
                if response.status_code == 200:
                    with destination_path.open("wb") as f:
                        f.write(response.content)
                    logger.info(f"Saved file via direct download to {destination_path}")
                    return str(destination_path)
            except httpx.HTTPError as e:
                logger.warning(
                    "Direct download failed for %s: %s (%s)",
                    remote_file_path,
                    str(e),
                    e.__class__.__name__,
                )

            signed_url = (
                f"{self.base_url}/signedUrl/download/{self.org_key}/{clean_path}"
            )

            try:
                response = await self._make_request(client, signed_url)
                if response.status_code == 200:
                    with destination_path.open("wb") as f:
                        f.write(response.content)
                    logger.info(f"Saved file via signed URL to {destination_path}")
                    return str(destination_path)
            except httpx.HTTPError as e:
                logger.error(
                    "Signed URL download failed for %s: %s (%s)",
                    remote_file_path,
                    str(e),
                    e.__class__.__name__,
                )
                raise UFADownloadError(
                    f"Failed to retrieve file from UFA after all attempts: {remote_file_path}"
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

    @beartype
    async def upload_file(
        self,
        *,
        local_file_path: str,
        remote_file_path: str,
    ) -> object:
        """
        Upload a single file to UFA using multipart/form-data via HTTP PUT.
        """

        if not os.path.isfile(local_file_path):
            raise FileNotFoundError(f"Local file does not exist: {local_file_path}")

        clean_remote_path = remote_file_path.lstrip("/")
        encoded_remote_path = quote(clean_remote_path, safe="/")
        url = f"{self.base_url}/{self.org_key}/{encoded_remote_path}"

        content_type, _ = mimetypes.guess_type(local_file_path)
        if not content_type:
            content_type = "application/octet-stream"
        if local_file_path.lower().endswith(".xml"):
            content_type = "text/xml"

        filename = os.path.basename(local_file_path)
        file_size_bytes = os.path.getsize(local_file_path)
        logger.info(
            "Preparing upload: url=%s filename=%s size_bytes=%s content_type=%s",
            url,
            filename,
            file_size_bytes,
            content_type,
        )

        timeout = httpx.Timeout(connect=30.0, read=300.0, write=300.0, pool=30.0)

        async with httpx.AsyncClient(timeout=timeout) as client:
            last_exception = None
            for attempt in range(1, self.max_retries + 1):
                try:
                    # use normal file handle, not async
                    with open(local_file_path, "rb") as fp:
                        files = {"file": (filename, fp, content_type)}
                        response = await client.put(
                            url, headers=self.headers, files=files
                        )
                    response.raise_for_status()

                    resp_ct = response.headers.get("content-type", "")
                    if "application/json" in resp_ct:
                        return response.json()
                    return response.text

                except httpx.HTTPError as e:
                    last_exception = e
                    logger.warning(
                        "Upload attempt %d failed for %s: %s (%s)",
                        attempt,
                        local_file_path,
                        str(e),
                        e.__class__.__name__,
                    )
                    if attempt < self.max_retries:
                        await anyio.sleep(2**attempt)
                    else:
                        break

        logger.error(
            "Upload failed after %d attempts: %s (%s)",
            self.max_retries,
            str(last_exception),
            last_exception.__class__.__name__ if last_exception else "UnknownError",
        )
        raise UFAUploadError(
            f"Failed to upload file to UFA: {local_file_path} -> {url}"
        ) from last_exception


class UFAError(Exception):
    """Base exception for UFA client errors."""


class UFADownloadError(UFAError):
    """Raised when downloading a file from UFA fails after retries."""


class UFAUploadError(UFAError):
    """Raised when uploading a file to UFA fails after retries."""
