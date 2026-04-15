"""Brands resource: list, create, update, delete brand profiles."""

from __future__ import annotations

from somanylemons.http import SyncTransport
from somanylemons.models.brands import Brand, BrandCreate, BrandSource


class BrandsResource:
    """Access to /api/v1/brands."""

    def __init__(self, transport: SyncTransport) -> None:
        self._t = transport

    def list(self) -> list[Brand]:
        data = self._t.request("GET", "/api/v1/brands")
        return [Brand(**item) for item in data.get("profiles", [])]

    def create(
        self,
        *,
        name: str,
        primary_color: str,
        secondary_color: str,
        accent_color: str | None = None,
        background_color: str | None = None,
        text_color: str | None = None,
        font_family: str | None = None,
        logo_url: str | None = None,
        is_default: bool | None = None,
        source: BrandSource | str = BrandSource.USER,
    ) -> Brand:
        """Create a new brand profile.

        For lead/outreach brands, pass ``source="lead"`` so the UI tags it
        separately from user-owned brands.
        """
        payload = BrandCreate(
            name=name,
            primary_color=primary_color,
            secondary_color=secondary_color,
            accent_color=accent_color,
            background_color=background_color,
            text_color=text_color,
            font_family=font_family,
            logo_url=logo_url,
            is_default=is_default,
            source=BrandSource(source) if isinstance(source, str) else source,
        ).model_dump(exclude_none=True, mode="json")
        data = self._t.request("POST", "/api/v1/brands", json=payload)
        return Brand(**data["profile"])

    def update(self, brand_id: int, **fields) -> Brand:
        """Update fields on an existing brand profile."""
        data = self._t.request("PUT", f"/api/v1/brands/{brand_id}", json=fields)
        return Brand(**(data.get("profile") or data))

    def delete(self, brand_id: int) -> None:
        self._t.request("DELETE", f"/api/v1/brands/{brand_id}")
