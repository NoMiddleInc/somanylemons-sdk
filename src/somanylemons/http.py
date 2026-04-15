"""HTTP transport layer for the SDK.

Handles authentication, retries with exponential backoff, rate-limit
awareness (respects ``Retry-After``), and maps HTTP errors to typed SDK
exceptions. Both sync and async clients share the same retry/error logic
via ``_classify_response``.

Security posture:
    * API keys are stored inside the client object but hidden from ``repr``
      and never included in log records.
    * ``base_url`` must be HTTPS unless the caller explicitly opts in to
      insecure transport (``allow_insecure_http=True``) — e.g. local dev.
    * By default only hostnames ending in ``.somanylemons.com`` (plus
      ``localhost``) are accepted. Arbitrary hosts require
      ``allow_foreign_host=True`` so the API key cannot be sent to an
      unintended server by mistake.
"""

from __future__ import annotations

import logging
import random
import time
from typing import Any
from urllib.parse import urlparse

import httpx

from somanylemons.errors import (
    AuthError,
    NotFoundError,
    PermissionError,
    QuotaError,
    RateLimitError,
    ServerError,
    SMLError,
    ValidationError,
)

logger = logging.getLogger("somanylemons")

DEFAULT_BASE_URL = "https://api.somanylemons.com"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
_RETRYABLE_STATUS = {429, 500, 502, 503, 504}

# Hosts that never require opt-in for API key transmission.
_TRUSTED_HOST_SUFFIXES: tuple[str, ...] = (".somanylemons.com",)
_TRUSTED_HOSTS: tuple[str, ...] = ("somanylemons.com", "localhost", "127.0.0.1")


def _validate_base_url(
    base_url: str,
    *,
    allow_insecure_http: bool,
    allow_foreign_host: bool,
) -> str:
    """Reject misconfigurations that would leak the API key.

    Returns the normalized base URL (trailing slash stripped).
    Raises ``SMLError`` when the URL is unsafe and the caller did not opt in.
    """
    parsed = urlparse(base_url)
    if parsed.scheme not in ("http", "https"):
        raise SMLError(f"Invalid base_url scheme: {parsed.scheme!r} (expected http/https)")
    if parsed.scheme == "http" and not allow_insecure_http:
        raise SMLError(
            "base_url uses plain HTTP. API keys would travel unencrypted. "
            "Pass allow_insecure_http=True to override (e.g. for localhost dev)."
        )
    host = (parsed.hostname or "").lower()
    if not host:
        raise SMLError(f"Invalid base_url: no host in {base_url!r}")
    is_trusted = (
        host in _TRUSTED_HOSTS
        or any(host.endswith(suffix) for suffix in _TRUSTED_HOST_SUFFIXES)
    )
    if not is_trusted and not allow_foreign_host:
        raise SMLError(
            f"base_url host {host!r} is not a SoManyLemons domain. "
            "Sending your API key to a foreign host is rejected by default. "
            "Pass allow_foreign_host=True if this is intentional."
        )
    return base_url.rstrip("/")


def _classify_response(response: httpx.Response) -> None:
    """Raise the right SDK exception for a non-2xx response. Returns on 2xx.

    Keeps the classification logic in one place so the sync and async clients
    behave identically.
    """
    if response.is_success:
        return

    body: Any
    try:
        body = response.json()
    except ValueError:
        body = {"raw": response.text}

    message = _extract_message(body) or f"HTTP {response.status_code}"
    status = response.status_code

    if status == 400:
        field_errors = _extract_field_errors(body)
        raise ValidationError(
            message, status_code=status, response_body=body, field_errors=field_errors
        )
    if status == 401:
        raise AuthError(message, status_code=status, response_body=body)
    if status == 403:
        # Differentiate quota from generic permission error if the server signals it.
        detail = (body.get("detail") or "").lower() if isinstance(body, dict) else ""
        if "quota" in detail or "render_limit" in (body if isinstance(body, dict) else {}):
            raise QuotaError(
                message,
                renders_used=body.get("renders_used") if isinstance(body, dict) else None,
                render_limit=body.get("render_limit") if isinstance(body, dict) else None,
                response_body=body,
            )
        raise PermissionError(message, status_code=status, response_body=body)
    if status == 404:
        raise NotFoundError(message, status_code=status, response_body=body)
    if status == 429:
        retry_after = _parse_retry_after(response.headers.get("Retry-After"))
        raise RateLimitError(message, retry_after=retry_after, response_body=body)
    if 500 <= status < 600:
        raise ServerError(message, status_code=status, response_body=body)

    raise SMLError(message, status_code=status, response_body=body)


def _extract_message(body: Any) -> str | None:
    if isinstance(body, dict):
        for key in ("detail", "message", "error"):
            val = body.get(key)
            if isinstance(val, str) and val:
                return val
    return None


def _extract_field_errors(body: Any) -> dict[str, list[str]]:
    """DRF validation errors look like {"field": ["msg1", "msg2"], ...}."""
    if not isinstance(body, dict):
        return {}
    return {
        k: v if isinstance(v, list) else [str(v)]
        for k, v in body.items()
        if k not in ("detail", "message", "error")
        and (isinstance(v, list) or isinstance(v, str))
    }


def _parse_retry_after(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def compute_backoff(attempt: int, retry_after: float | None = None, *, jitter: bool = True) -> float:
    """Return the number of seconds to wait before retry attempt ``attempt``.

    Prefers the server's Retry-After hint when present. Otherwise uses
    exponential backoff capped at 30 seconds with optional jitter.
    """
    if retry_after is not None:
        return max(0.0, retry_after)
    base = min(2 ** attempt, 30)
    if jitter:
        return base + random.uniform(0, base * 0.25)
    return float(base)


def _mask_key(api_key: str) -> str:
    """Return a short, non-recoverable preview of a key for logs / repr."""
    if not api_key:
        return "(empty)"
    prefix = api_key[:8]
    return f"{prefix}…(redacted)"


class _SecretStr:
    """Wraps a secret so it survives equality checks but never leaks into
    ``repr`` / ``str`` / logging output.

    Code that needs the raw value calls ``.get()`` explicitly, which makes
    accidental leaks grep-able during review.
    """

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        self._value = value

    def get(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"_SecretStr({_mask_key(self._value)})"

    def __str__(self) -> str:
        return _mask_key(self._value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _SecretStr):
            return self._value == other._value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)


class SyncTransport:
    """Sync HTTP transport with retries and typed error handling."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        allow_insecure_http: bool = False,
        allow_foreign_host: bool = False,
        client: httpx.Client | None = None,
    ) -> None:
        if not api_key:
            raise AuthError("API key is required")
        self._api_key = _SecretStr(api_key)
        self.base_url = _validate_base_url(
            base_url,
            allow_insecure_http=allow_insecure_http,
            allow_foreign_host=allow_foreign_host,
        )
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = client or httpx.Client(
            base_url=self.base_url,
            headers={"X-API-Key": api_key},
            timeout=timeout,
        )
        self._owns_client = client is None

    @property
    def api_key_prefix(self) -> str:
        """Non-sensitive preview of the configured key for diagnostics."""
        return _mask_key(self._api_key.get())

    def __repr__(self) -> str:
        return (
            f"<SyncTransport base_url={self.base_url!r} "
            f"api_key={self.api_key_prefix}>"
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> Any:
        attempt = 0
        while True:
            try:
                response = self._client.request(
                    method, path, json=json, params=params, files=files, data=data
                )
                _classify_response(response)
                if response.status_code == 204 or not response.content:
                    return None
                return response.json()
            except (RateLimitError, ServerError) as exc:
                if attempt >= self.max_retries:
                    raise
                retry_after = getattr(exc, "retry_after", None)
                delay = compute_backoff(attempt, retry_after)
                logger.info(
                    "sml_sdk_retry",
                    extra={
                        "method": method,
                        "path": path,
                        "attempt": attempt + 1,
                        "delay": delay,
                        "reason": type(exc).__name__,
                    },
                )
                time.sleep(delay)
                attempt += 1
            except httpx.TimeoutException:
                if attempt >= self.max_retries:
                    raise
                time.sleep(compute_backoff(attempt))
                attempt += 1

    def close(self) -> None:
        if self._owns_client:
            self._client.close()


class AsyncTransport:
    """Async counterpart of SyncTransport. Same retry logic, async primitives."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        allow_insecure_http: bool = False,
        allow_foreign_host: bool = False,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        if not api_key:
            raise AuthError("API key is required")
        self._api_key = _SecretStr(api_key)
        self.base_url = _validate_base_url(
            base_url,
            allow_insecure_http=allow_insecure_http,
            allow_foreign_host=allow_foreign_host,
        )
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = client or httpx.AsyncClient(
            base_url=self.base_url,
            headers={"X-API-Key": api_key},
            timeout=timeout,
        )
        self._owns_client = client is None

    @property
    def api_key_prefix(self) -> str:
        return _mask_key(self._api_key.get())

    def __repr__(self) -> str:
        return (
            f"<AsyncTransport base_url={self.base_url!r} "
            f"api_key={self.api_key_prefix}>"
        )

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> Any:
        import asyncio

        attempt = 0
        while True:
            try:
                response = await self._client.request(
                    method, path, json=json, params=params, files=files, data=data
                )
                _classify_response(response)
                if response.status_code == 204 or not response.content:
                    return None
                return response.json()
            except (RateLimitError, ServerError) as exc:
                if attempt >= self.max_retries:
                    raise
                retry_after = getattr(exc, "retry_after", None)
                await asyncio.sleep(compute_backoff(attempt, retry_after))
                attempt += 1
            except httpx.TimeoutException:
                if attempt >= self.max_retries:
                    raise
                await asyncio.sleep(compute_backoff(attempt))
                attempt += 1

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()
