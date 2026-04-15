"""Image quote resource: render branded quote images."""

from __future__ import annotations

from somanylemons.http import SyncTransport
from somanylemons.models.image_quote import (
    ImageQuoteArchetype,
    ImageQuoteRequest,
    ImageQuoteResult,
    ImageQuoteSize,
)


class ImageQuoteResource:
    """Access to POST /api/v1/image-quote."""

    def __init__(self, transport: SyncTransport) -> None:
        self._t = transport

    def create(
        self,
        *,
        quote_text: str,
        brand_profile_id: int | None = None,
        speaker_name: str | None = None,
        speaker_title: str | None = None,
        size: ImageQuoteSize | str = ImageQuoteSize.SQUARE,
        template_id: int | None = None,
        archetype: ImageQuoteArchetype | str | None = None,
        draft_id: int | None = None,
    ) -> ImageQuoteResult:
        """Render a branded image quote.

        For predictable output across many calls (e.g. outreach batches),
        pass ``template_id`` to pin a specific template. Without it, the AI
        picker chooses from the top candidates.
        """
        payload = ImageQuoteRequest(
            quote_text=quote_text,
            brand_profile_id=brand_profile_id,
            speaker_name=speaker_name,
            speaker_title=speaker_title,
            size=ImageQuoteSize(size) if isinstance(size, str) else size,
            template_id=template_id,
            archetype=ImageQuoteArchetype(archetype)
            if isinstance(archetype, str)
            else archetype,
            draft_id=draft_id,
        ).model_dump(exclude_none=True, mode="json")
        data = self._t.request("POST", "/api/v1/image-quote", json=payload)
        return ImageQuoteResult(**data)
