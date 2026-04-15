"""Drafts resource: manage the content queue."""

from __future__ import annotations

from somanylemons.http import SyncTransport
from somanylemons.models.drafts import Draft, DraftStatus


class DraftsResource:
    """Access to /api/v1/drafts."""

    def __init__(self, transport: SyncTransport) -> None:
        self._t = transport

    def list(
        self,
        *,
        limit: int = 20,
        status: DraftStatus | str | None = None,
    ) -> list[Draft]:
        params: dict = {"limit": limit}
        if status is not None:
            params["status"] = status.value if isinstance(status, DraftStatus) else status
        data = self._t.request("GET", "/api/v1/drafts", params=params)
        return [Draft(**item) for item in data.get("drafts", [])]

    def create(self, *, caption: str, job_id: str | None = None) -> Draft:
        """Create a draft. Pass ``job_id`` to attach media from a completed render."""
        payload = {"caption": caption}
        if job_id is not None:
            payload["job_id"] = job_id
        data = self._t.request("POST", "/api/v1/drafts", json=payload)
        return Draft(**data)
