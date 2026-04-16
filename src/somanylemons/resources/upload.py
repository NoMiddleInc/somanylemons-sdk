"""Upload resource: upload local files to get hosted URLs."""

from __future__ import annotations

import mimetypes
from pathlib import Path

from somanylemons.http import SyncTransport


class UploadResource:
    """Access to POST /api/v1/upload.

    Upload local files (logos, headshots, short recordings) to get a
    publicly-accessible URL you can pass to other endpoints.
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._t = transport

    def upload_file(self, file_path: str | Path) -> str:
        """Upload a local file and return the hosted URL.

        Args:
            file_path: Path to the file on disk (image, audio, or video, max 50MB).

        Returns:
            The public URL of the uploaded file.

        Raises:
            FileNotFoundError: if the file doesn't exist.
            SMLError: on upload failure.
        """
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        with path.open("rb") as fh:
            data = self._t.request(
                "POST",
                "/api/v1/upload",
                files={"file": (path.name, fh, content_type)},
            )
        return data.get("url") or data.get("file_url") or ""
