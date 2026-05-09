"""Templates resource: list available video/image templates."""

from __future__ import annotations

from somanylemons.http import SyncTransport
from somanylemons.models.templates import Template


class TemplatesResource:
    """Access to GET /api/v1/templates."""

    def __init__(self, transport: SyncTransport) -> None:
        self._t = transport

    def list(
        self,
        *,
        asset_type: str | None = None,
        orientation: str | None = None,
        size: str | None = None,
    ) -> list[Template]:
        """List all active templates available for the organization.

        Use the template ``id`` with ``image_quotes.create(template_id=...)``
        or ``reels.create(...)`` to pin a specific visual output.
        """
        params = {
            key: value
            for key, value in {
                "asset_type": asset_type,
                "orientation": orientation,
                "size": size,
            }.items()
            if value is not None
        }
        data = self._t.request("GET", "/api/v1/templates", params=params or None)
        return [Template(**item) for item in data.get("templates", [])]
