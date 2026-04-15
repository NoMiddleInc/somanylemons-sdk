"""Models for /api/v1/drafts."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class DraftStatus(str, Enum):
    DRAFT = "draft"
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    POSTED = "posted"


class Draft(BaseModel):
    """A draft post in the content queue."""

    model_config = ConfigDict(extra="allow")

    id: int
    caption: str = ""
    status: DraftStatus = DraftStatus.DRAFT
    media_url: str | None = None
    media_thumb: str | None = None
    content_type: str | None = None
    engagement_scores: dict | None = None
    scheduled_for: datetime | None = None
    created_at: datetime | None = None
    share_url: str | None = None


class DraftCreate(BaseModel):
    """Payload for POST /api/v1/drafts."""

    caption: str = Field(..., min_length=1)
    job_id: str | None = None
