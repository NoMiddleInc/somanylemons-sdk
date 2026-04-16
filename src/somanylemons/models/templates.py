"""Models for GET /api/v1/templates."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Template(BaseModel):
    """A video/image template available for rendering."""

    model_config = ConfigDict(extra="allow")

    id: int
    name: str
    caption_style: str | None = None
    thumbnail: str | None = None
    width: int = 1080
    height: int = 1920
