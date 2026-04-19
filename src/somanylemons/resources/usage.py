"""Usage resource: check render quota and billing period stats."""

from __future__ import annotations

from somanylemons.http import SyncTransport
from somanylemons.models.usage import Usage


class UsageResource:
    """Access to GET /api/v1/usage."""

    def __init__(self, transport: SyncTransport) -> None:
        self._t = transport

    def get(self) -> Usage:
        """Return the current billing period usage summary.

        Includes renders used/remaining, tier, and per-event-type counts.
        """
        data = self._t.request("GET", "/api/v1/usage")
        return Usage(**data)
