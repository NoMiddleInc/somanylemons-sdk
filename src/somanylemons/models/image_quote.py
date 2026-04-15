"""Models for POST /api/v1/image-quote."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ImageQuoteArchetype(str, Enum):
    QUOTE_HERO = "QUOTE_HERO"
    STAT = "STAT"
    TESTIMONIAL = "TESTIMONIAL"
    EVENT = "EVENT"
    PRESS = "PRESS"
    COLLAGE = "COLLAGE"


class ImageQuoteSize(str, Enum):
    SQUARE = "square"
    PORTRAIT = "portrait"
    HORIZONTAL = "horizontal"


class ImageQuoteRequest(BaseModel):
    """Payload for POST /api/v1/image-quote."""

    model_config = ConfigDict(extra="forbid")

    quote_text: str = Field(..., min_length=1)
    brand_profile_id: int | None = None
    speaker_name: str | None = None
    speaker_title: str | None = None
    size: ImageQuoteSize = ImageQuoteSize.SQUARE
    template_id: int | None = None
    archetype: ImageQuoteArchetype | None = None
    draft_id: int | None = None


class ImageQuoteResult(BaseModel):
    """Response from POST /api/v1/image-quote."""

    model_config = ConfigDict(extra="allow")

    success: bool
    image_url: str | None = None
    media_id: int | None = None
    draft_id: int | None = None
