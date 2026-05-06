"""Pydantic models for SoManyLemons API payloads.

Models are strict by default (extra fields allowed for forward-compatibility
but logged at the client layer) and use explicit types so IDE autocomplete
works correctly.
"""

from somanylemons.models.brands import Brand, BrandCreate, BrandSource
from somanylemons.models.drafts import Draft, DraftCreate, DraftStatus
from somanylemons.models.image_quote import ImageQuoteRequest, ImageQuoteResult
from somanylemons.models.jobs import (
    ClipSource,
    Job,
    JobClip,
    JobStatus,
    UploadedBy,
)
from somanylemons.models.reels import (
    AssetType,
    Background,
    BackgroundType,
    CaptionConfig,
    CaptionStyle,
    ReelsCreate,
    ReelsResponse,
)
from somanylemons.models.templates import Template
from somanylemons.models.usage import Usage

__all__ = [
    "Brand",
    "BrandCreate",
    "BrandSource",
    "Draft",
    "DraftCreate",
    "DraftStatus",
    "ImageQuoteRequest",
    "ImageQuoteResult",
    "ClipSource",
    "Job",
    "JobClip",
    "JobStatus",
    "UploadedBy",
    "AssetType",
    "Background",
    "BackgroundType",
    "CaptionConfig",
    "CaptionStyle",
    "ReelsCreate",
    "ReelsResponse",
    "Template",
    "Usage",
]
