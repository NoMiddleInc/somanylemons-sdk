"""Jobs resource: list recordings, get details, poll until done."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from somanylemons.errors import JobFailedError, TimeoutError as SMLTimeoutError
from somanylemons.http import SyncTransport
from somanylemons.models.jobs import Job, JobStatus


class JobsResource:
    """Access to /api/v1/jobs and /api/v1/clip/{id}."""

    def __init__(self, transport: SyncTransport) -> None:
        self._t = transport

    def list(
        self,
        *,
        limit: int = 20,
        status: JobStatus | str | None = None,
        source: str | None = None,
        include: str | None = None,
    ) -> list[Job]:
        """List recent recordings. Returns compact Job models (no clips array).

        Use :meth:`get` to fetch full clip details for a specific job.
        """
        params: dict[str, Any] = {"limit": limit}
        if status is not None:
            params["status"] = status.value if isinstance(status, JobStatus) else status
        if source is not None:
            params["source"] = source
        if include is not None:
            params["include"] = include
        data = self._t.request("GET", "/api/v1/jobs", params=params)
        return [Job(**item) for item in data.get("jobs", [])]

    def get(self, job_id: str | int) -> Job:
        """Fetch a single recording with full clip details."""
        data = self._t.request("GET", f"/api/v1/clip/{job_id}")
        return Job(**data)

    def wait_for(
        self,
        job_id: str | int,
        *,
        timeout: float = 600.0,
        poll_interval: float = 5.0,
        on_progress: Callable[[Job], None] | None = None,
    ) -> Job:
        """Poll until the job reaches a terminal state or timeout elapses.

        Args:
            job_id: ID of the Clip or RenderJob to poll.
            timeout: Seconds to wait before giving up.
            poll_interval: Seconds between polls.
            on_progress: Optional callback invoked after each poll with the
                current Job. Useful for showing progress bars.

        Returns:
            The final Job once status is completed.

        Raises:
            JobFailedError: if the job finished with status=failed.
            SMLTimeoutError: if the deadline elapses before completion.
        """
        deadline = time.monotonic() + timeout
        job: Job | None = None
        while time.monotonic() < deadline:
            job = self.get(job_id)
            if on_progress:
                on_progress(job)
            if job.status == JobStatus.COMPLETED:
                return job
            if job.status == JobStatus.FAILED:
                raise JobFailedError(
                    job.error or f"Job {job_id} failed", job=job
                )
            time.sleep(poll_interval)
        raise SMLTimeoutError(
            f"Job {job_id} did not complete within {timeout}s "
            f"(last status: {job.status.value if job else 'unknown'})"
        )
