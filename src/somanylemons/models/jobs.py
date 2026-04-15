"""Models for GET /api/v1/jobs and GET /api/v1/clip/{id}."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class JobStatus(str, Enum):
    """Processing status for a Clip or RenderJob."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ClipSource(str, Enum):
    """Where the underlying Clip was created."""

    API = "api"
    WEB = "web"


class UploadedBy(BaseModel):
    """Lightweight user descriptor for the clip owner."""

    model_config = ConfigDict(extra="allow")

    id: int | None = None
    name: str | None = None
    email: str | None = None


class JobClip(BaseModel):
    """A single rendered clip produced from a Job."""

    model_config = ConfigDict(extra="allow")

    id: str
    url: str | None = None
    thumbnail_url: str | None = None
    duration_seconds: float | None = None
    transcript: str | None = None


class Job(BaseModel):
    """A recording (Clip) as returned by /api/v1/jobs or /api/v1/clip/{id}.

    The list endpoint returns a compact view (no ``clips``, short ``transcript_preview``).
    The detail endpoint returns the full view with ``clips`` populated.
    """

    model_config = ConfigDict(extra="allow")

    id: str
    title: str = ""
    status: JobStatus = JobStatus.PENDING
    progress: int = 0
    source: ClipSource | None = None
    source_type: str | None = None
    input_type: str | None = None
    duration_seconds: float | None = None
    transcript_preview: str = ""
    uploaded_by: UploadedBy | None = None
    clip_count: int | None = None
    clips: list[JobClip] = Field(default_factory=list)
    error: str | None = None
    created_at: datetime | str | None = None

    @property
    def is_terminal(self) -> bool:
        """True when the job has finished (either completed or failed)."""
        return self.status in (JobStatus.COMPLETED, JobStatus.FAILED)

    @property
    def is_successful(self) -> bool:
        return self.status == JobStatus.COMPLETED
