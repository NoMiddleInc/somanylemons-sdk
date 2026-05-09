"""Models for GET /api/v1/templates."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Template(BaseModel):
    """A video/image template available for rendering."""

    model_config = ConfigDict(extra="allow")

    id: int
    name: str
    template_key: str | None = None
    model: str | None = None
    asset_type: str | None = None
    caption_style: str | None = None
    size: str | None = None
    thumbnail_url: str | None = None
    preview_video_url: str | None = None
    source: str | None = None
    width: int = 1080
    height: int = 1920
