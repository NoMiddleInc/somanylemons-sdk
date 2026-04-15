"""Transcribe resource: kick off transcription jobs for media."""

from __future__ import annotations

import mimetypes
from collections.abc import Callable
from pathlib import Path

from somanylemons.http import SyncTransport
from somanylemons.models.jobs import Job
from somanylemons.resources.jobs import JobsResource


class TranscribeResource:
    """Access to POST /api/v1/transcribe."""

    def __init__(self, transport: SyncTransport, jobs: JobsResource) -> None:
        self._t = transport
        self._jobs = jobs

    def create(
        self,
        *,
        url: str | None = None,
        file_path: str | Path | None = None,
    ) -> dict:
        """Submit media for transcription. Returns the raw API response
        with ``clip_id`` and polling URL. Use :meth:`create_and_wait` to block
        until the transcript is ready.
        """
        if bool(url) == bool(file_path):
            raise ValueError("Provide exactly one of 'url' or 'file_path'.")

        if file_path is not None:
            path = Path(file_path)
            content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            with path.open("rb") as fh:
                return self._t.request(
                    "POST",
                    "/api/v1/transcribe",
                    files={"file": (path.name, fh, content_type)},
                )
        return self._t.request("POST", "/api/v1/transcribe", json={"url": url})

    def create_and_wait(
        self,
        *,
        timeout: float = 900.0,
        poll_interval: float = 10.0,
        on_progress: Callable[[Job], None] | None = None,
        **create_kwargs,
    ) -> Job:
        """Submit transcription and wait for the resulting Clip to finish."""
        initial = self.create(**create_kwargs)
        clip_id = initial.get("clip_id")
        if not clip_id:
            raise ValueError(
                f"Transcribe response missing 'clip_id': {initial!r}"
            )
        return self._jobs.wait_for(
            clip_id,
            timeout=timeout,
            poll_interval=poll_interval,
            on_progress=on_progress,
        )
