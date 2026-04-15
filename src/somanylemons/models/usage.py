"""Models for GET /api/v1/usage and related account endpoints."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Usage(BaseModel):
    """Current billing-period usage summary."""

    model_config = ConfigDict(extra="allow")

    billing_period: str
    tier: str
    render_limit: int
    renders_used: int
    renders_remaining: int
    has_metered_billing: bool = False
    counts: dict[str, int] = {}
