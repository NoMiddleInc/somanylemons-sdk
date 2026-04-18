"""SoManyLemons Python SDK.

Thin, typed wrapper over the SoManyLemons Public API
(https://api.somanylemons.com/api/v1). Gives you a single ``SMLClient`` with
typed resources for brands, reels, image quotes, drafts, transcription, and
content generation.

Quickstart:
    >>> from somanylemons import SMLClient
    >>> client = SMLClient(api_key="sml_xxx")
    >>> job = client.reels.create_and_wait(
    ...     url="https://example.com/recording.mp4",
    ...     brand_profile_id=1,
    ...     caption_style="LEMON",
    ... )
    >>> print(job.clips[0].url)
"""

from somanylemons.client import SMLClient
from somanylemons.errors import (
    AuthError,
    JobFailedError,
    NotFoundError,
    PermissionError,
    QuotaError,
    RateLimitError,
    ServerError,
    SMLError,
    TimeoutError,
    ValidationError,
)
from somanylemons.models import (
    Background,
    BackgroundType,
    Brand,
    BrandCreate,
    BrandSource,
    CaptionConfig,
    CaptionStyle,
    ClipSource,
    Draft,
    DraftCreate,
    DraftStatus,
    ImageQuoteRequest,
    ImageQuoteResult,
    Job,
    JobClip,
    JobStatus,
    ReelsCreate,
    ReelsResponse,
    Template,
    UploadedBy,
    Usage,
)

__version__ = "0.1.2"

__all__ = [
    # Client
    "SMLClient",
    # Errors
    "SMLError",
    "AuthError",
    "PermissionError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "QuotaError",
    "ServerError",
    "TimeoutError",
    "JobFailedError",
    # Models — Jobs
    "Job",
    "JobClip",
    "JobStatus",
    "ClipSource",
    "UploadedBy",
    # Models — Brands
    "Brand",
    "BrandCreate",
    "BrandSource",
    # Models — Reels
    "ReelsCreate",
    "ReelsResponse",
    "Background",
    "BackgroundType",
    "CaptionConfig",
    "CaptionStyle",
    # Models — Image Quote
    "ImageQuoteRequest",
    "ImageQuoteResult",
    # Models — Drafts
    "Draft",
    "DraftCreate",
    "DraftStatus",
    # Models — Templates
    "Template",
    # Models — Usage
    "Usage",
]
