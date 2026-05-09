"""Reels resource: submit recordings for branded clip creation."""

from __future__ import annotations

import mimetypes
from collections.abc import Callable, Sequence
from pathlib import Path

from somanylemons.http import SyncTransport
from somanylemons.models.jobs import Job
from somanylemons.models.reels import (
    Background,
    CaptionConfig,
    CaptionStyle,
    AssetType,
    ReelsCreate,
    ReelsResponse,
)
from somanylemons.resources.jobs import JobsResource


class ReelsResource:
    """Access to POST /api/v1/clip (submit) and chained polling helpers."""

    def __init__(self, transport: SyncTransport, jobs: JobsResource) -> None:
        self._t = transport
        self._jobs = jobs

    def create(
        self,
        *,
        url: str | None = None,
        file_path: str | Path | None = None,
        brand_profile_id: int | None = None,
        asset_types: Sequence[AssetType | str] | None = None,
        caption_style: CaptionStyle | str | None = None,
        background: Background | dict | None = None,
        logo_url: str | None = None,
        headshot_url: str | None = None,
        caption_config: CaptionConfig | dict | None = None,
        orientation: str | None = None,
        show_speaker: bool | None = None,
        show_headshot: bool | None = None,
        template_ids: dict[str, int | str] | None = None,
        webhook_url: str | None = None,
    ) -> ReelsResponse:
        """Submit a recording for rendering.

        Provide exactly one of ``url`` or ``file_path``. Returns immediately
        with a job ID; use :meth:`create_and_wait` if you want to block until
        the render finishes.
        """
        if bool(url) == bool(file_path):
            raise ValueError("Provide exactly one of 'url' or 'file_path'.")

        if file_path is not None:
            data = self._build_multipart_fields(
                brand_profile_id=brand_profile_id,
                asset_types=asset_types,
                caption_style=caption_style,
                logo_url=logo_url,
                headshot_url=headshot_url,
                orientation=orientation,
                show_speaker=show_speaker,
                show_headshot=show_headshot,
                asset_types=asset_types,
                template_ids=template_ids,
                webhook_url=webhook_url,
            )
            path = Path(file_path)
            content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            with path.open("rb") as fh:
                response = self._t.request(
                    "POST",
                    "/api/v1/clip",
                    files={"file": (path.name, fh, content_type)},
                    data=data,
                )
        else:
            payload = ReelsCreate(
                url=url,
                brand_profile_id=brand_profile_id,
                asset_types=self._normalize_asset_types(asset_types),
                caption_style=CaptionStyle(caption_style)
                if isinstance(caption_style, str)
                else caption_style,
                background=Background(**background) if isinstance(background, dict) else background,
                logo_url=logo_url,
                headshot_url=headshot_url,
                caption_config=CaptionConfig(**caption_config)
                if isinstance(caption_config, dict)
                else caption_config,
                orientation=orientation,
                show_speaker=show_speaker,
                show_headshot=show_headshot,
                asset_types=asset_types,
                template_ids=template_ids,
                webhook_url=webhook_url,
            ).model_dump(exclude_none=True, mode="json")
            response = self._t.request("POST", "/api/v1/clip", json=payload)

        return ReelsResponse(**response)

    def create_and_wait(
        self,
        *,
        timeout: float = 600.0,
        poll_interval: float = 10.0,
        on_progress: Callable[[Job], None] | None = None,
        **create_kwargs,
    ) -> Job:
        """Shortcut: submit and block until the render finishes.

        All keyword arguments after ``timeout`` / ``poll_interval`` /
        ``on_progress`` are forwarded to :meth:`create`.
        """
        initial = self.create(**create_kwargs)
        return self._jobs.wait_for(
            initial.id,
            timeout=timeout,
            poll_interval=poll_interval,
            on_progress=on_progress,
        )

    @staticmethod
    def _build_multipart_fields(**kwargs) -> dict[str, str | list[str]]:
        """Serialize kwargs as multipart form strings, skipping None values."""
        out: dict[str, str | list[str]] = {}
        for key, val in kwargs.items():
            if val is None:
                continue
            if isinstance(val, CaptionStyle | AssetType):
                out[key] = val.value
            elif isinstance(val, Sequence) and not isinstance(val, str):
                out[key] = ",".join(
                    item.value if isinstance(item, AssetType) else str(item)
                    for item in val
                )
            elif isinstance(val, bool):
                out[key] = "true" if val else "false"
            else:
                out[key] = str(val)
        return out

    @staticmethod
    def _normalize_asset_types(
        asset_types: Sequence[AssetType | str] | None,
    ) -> list[AssetType] | None:
        if asset_types is None:
            return None
        return [
            AssetType(asset_type) if isinstance(asset_type, str) else asset_type
            for asset_type in asset_types
        ]
