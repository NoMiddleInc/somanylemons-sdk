"""Models for POST /api/v1/clip (create reels)."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CaptionStyle(str, Enum):
    """Caption animation style presets.

    Mirrors the 8 valid styles in the backend. Unknown styles will be rejected
    by the server with a 400.
    """

    LEMON = "LEMON"
    VITAMIN_C = "VITAMIN_C"
    PLAIN = "PLAIN"
    SPOTLIGHT = "SPOTLIGHT"
    GLITCH = "GLITCH"
    RANSOM = "RANSOM"
    WAVE = "WAVE"
    BOUNCE = "BOUNCE"


class AssetType(str, Enum):
    """Rendered asset types for API-created clips.

    If omitted, the API defaults to ``videogram``.
    """

    VIDEOGRAM = "videogram"
    AUDIOGRAM = "audiogram"
    IMAGE_QUOTE = "image_quote"


class BackgroundType(str, Enum):
    SOLID = "solid"
    IMAGE = "image"
    VIDEO = "video"
    GRADIENT = "gradient"


class Background(BaseModel):
    """Background configuration for a reel render."""

    model_config = ConfigDict(extra="forbid")

    type: BackgroundType = BackgroundType.SOLID
    color: str | None = None
    image_url: str | None = None
    image_fit: str | None = None
    video_url: str | None = None
    gradient: dict[str, Any] | None = None


class CaptionConfig(BaseModel):
    """Fine-tuning over the style preset. All fields optional."""

    model_config = ConfigDict(extra="forbid")

    text_color: str | None = None
    highlight_color: str | None = None
    font_size: int | None = Field(default=None, ge=12, le=200)
    font_family: str | None = None
    stroke_color: str | None = None
    stroke_width: int | None = Field(default=None, ge=0, le=20)
    background_color: str | None = None
    background_opacity: float | None = Field(default=None, ge=0.0, le=1.0)
    text_transform: str | None = None
    max_words_per_phrase: int | None = Field(default=None, ge=1, le=10)
    style_params: dict[str, Any] | None = None


class ReelsCreate(BaseModel):
    """Payload for POST /api/v1/clip.

    Provide ``url`` for a public URL source, OR use ``file_path`` with the
    client's file-upload helper (the helper will set multipart fields, not
    send this model as JSON).
    """

    model_config = ConfigDict(extra="forbid")

    url: str | None = None
    brand_profile_id: int | None = None
    asset_types: list[AssetType] | None = None
    caption_style: CaptionStyle | None = None
    background: Background | None = None
    logo_url: str | None = None
    headshot_url: str | None = None
    caption_config: CaptionConfig | None = None
    orientation: str | None = None
    show_speaker: bool | None = None
    show_headshot: bool | None = None
    webhook_url: str | None = None
    composition_overrides: dict[str, Any] | None = None
    asset_types: list[str] | None = None
    template_ids: dict[str, int | str] | None = None


class ReelsResponse(BaseModel):
    """Response from POST /api/v1/clip."""

    model_config = ConfigDict(extra="allow")

    id: str
    status: str
    poll_url: str | None = None
