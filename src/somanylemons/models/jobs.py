"""Models for GET /api/v1/jobs and GET /api/v1/clip/{id}."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

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


class JobAsset(BaseModel):
    """A single rendered asset produced from a Job."""

    model_config = ConfigDict(extra="allow")

    id: str
    asset_type: str | None = None
    media_type: str | None = None
    template: dict[str, Any] | None = None
    url: str | None = None
    thumbnail_url: str | None = None
    duration_seconds: float | None = None
    transcript: str | None = None


class JobClip(JobAsset):
    """A legacy video-only rendered clip produced from a Job."""


class Job(BaseModel):
    """A recording (Clip) as returned by /api/v1/jobs or /api/v1/clip/{id}.

    The list endpoint returns a compact view (no render arrays, short
    ``transcript_preview``). The detail endpoint returns ``assets`` for every
    rendered asset and ``clips`` for the legacy video-only list.
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
    assets: list[JobAsset] = Field(default_factory=list)
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
