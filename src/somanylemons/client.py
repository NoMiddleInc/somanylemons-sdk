"""SMLClient: the entry point for all SDK interactions."""

from __future__ import annotations

import os
from types import TracebackType
from typing import Self

from somanylemons.http import DEFAULT_BASE_URL, DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT, SyncTransport
from somanylemons.resources.brands import BrandsResource
from somanylemons.resources.content import ContentResource
from somanylemons.resources.drafts import DraftsResource
from somanylemons.resources.image_quote import ImageQuoteResource
from somanylemons.resources.jobs import JobsResource
from somanylemons.resources.reels import ReelsResource
from somanylemons.resources.templates import TemplatesResource
from somanylemons.resources.transcribe import TranscribeResource
from somanylemons.resources.upload import UploadResource


class SMLClient:
    """Synchronous client for the SoManyLemons Public API.

    Usage:
        >>> from somanylemons import SMLClient
        >>> client = SMLClient(api_key="sml_xxx")
        >>> jobs = client.jobs.list(limit=5)
        >>> for job in jobs:
        ...     print(job.id, job.title)

    The client exposes resources as attributes (``client.jobs``, ``client.brands``,
    etc.). It is safe to share a single client across threads.

    Configuration precedence:
        1. Explicit constructor arguments
        2. Environment variables (``SML_API_KEY``, ``SML_API_URL``)
        3. Defaults (``DEFAULT_BASE_URL``)
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        allow_insecure_http: bool = False,
        allow_foreign_host: bool = False,
    ) -> None:
        resolved_key = api_key or os.environ.get("SML_API_KEY", "")
        resolved_base = base_url or os.environ.get("SML_API_URL") or DEFAULT_BASE_URL

        self._transport = SyncTransport(
            api_key=resolved_key,
            base_url=resolved_base,
            timeout=timeout,
            max_retries=max_retries,
            allow_insecure_http=allow_insecure_http,
            allow_foreign_host=allow_foreign_host,
        )

        self.jobs = JobsResource(self._transport)
        self.brands = BrandsResource(self._transport)
        self.drafts = DraftsResource(self._transport)
        self.image_quotes = ImageQuoteResource(self._transport)
        self.reels = ReelsResource(self._transport, self.jobs)
        self.templates = TemplatesResource(self._transport)
        self.transcribe = TranscribeResource(self._transport, self.jobs)
        self.upload = UploadResource(self._transport)
        self.content = ContentResource(self._transport)

    @property
    def base_url(self) -> str:
        return self._transport.base_url

    @property
    def api_key_prefix(self) -> str:
        """A short, non-sensitive preview of the active API key (for logs)."""
        return self._transport.api_key_prefix

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._transport.close()

    def __repr__(self) -> str:
        return (
            f"<SMLClient base_url={self.base_url!r} "
            f"api_key={self.api_key_prefix}>"
        )

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()
