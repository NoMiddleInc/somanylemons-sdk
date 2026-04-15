"""Models for /api/v1/brands."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class BrandSource(str, Enum):
    """Origin tag for a brand profile.

    - ``user``: created by an end user (default for web signups)
    - ``lead``: created programmatically for a prospect (outreach tooling)
    - ``system``: auto-generated placeholder
    """

    USER = "user"
    LEAD = "lead"
    SYSTEM = "system"


class Brand(BaseModel):
    """A brand profile returned by GET /api/v1/brands."""

    model_config = ConfigDict(extra="allow")

    id: int
    name: str
    logo_url: str | None = None
    primary_color: str = ""
    secondary_color: str = ""
    accent_color: str = ""
    background_color: str = ""
    text_color: str = ""
    font_family: str = "Arial"
    is_default: bool = False
    source: BrandSource = BrandSource.USER


class BrandCreate(BaseModel):
    """Payload for POST /api/v1/brands."""

    name: str = Field(..., min_length=1, max_length=255)
    primary_color: str
    secondary_color: str
    accent_color: str | None = None
    background_color: str | None = None
    text_color: str | None = None
    font_family: str | None = None
    logo_url: str | None = None
    is_default: bool | None = None
    source: BrandSource = BrandSource.USER
