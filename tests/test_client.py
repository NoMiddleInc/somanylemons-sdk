"""Smoke tests for the sync client using respx mocks."""

from __future__ import annotations

import json

import httpx
import json
import pytest
import respx

from somanylemons import (
    AuthError,
    NotFoundError,
    QuotaError,
    RateLimitError,
    SMLClient,
    ValidationError,
)


@pytest.fixture
def client() -> SMLClient:
    return SMLClient(api_key="sml_test_key", base_url="https://api.test.somanylemons.com")


@respx.mock
def test_list_jobs_parses_compact_response(client: SMLClient) -> None:
    respx.get("https://api.test.somanylemons.com/api/v1/jobs").mock(
        return_value=httpx.Response(
            200,
            json={
                "jobs": [
                    {
                        "id": "42",
                        "title": "Quote from last week",
                        "status": "completed",
                        "source": "api",
                        "clip_count": 3,
                        "transcript_preview": "hello...",
                        "created_at": "2026-04-15",
                    }
                ]
            },
        )
    )
    jobs = client.jobs.list(limit=10)
    assert len(jobs) == 1
    assert jobs[0].id == "42"
    assert jobs[0].clip_count == 3
    assert jobs[0].is_successful


@respx.mock
def test_auth_error_maps_401(client: SMLClient) -> None:
    respx.get("https://api.test.somanylemons.com/api/v1/brands").mock(
        return_value=httpx.Response(401, json={"detail": "Invalid key"})
    )
    with pytest.raises(AuthError) as exc_info:
        client.brands.list()
    assert exc_info.value.status_code == 401


@respx.mock
def test_not_found_maps_404(client: SMLClient) -> None:
    respx.get("https://api.test.somanylemons.com/api/v1/clip/9999").mock(
        return_value=httpx.Response(404, json={"detail": "Job not found"})
    )
    with pytest.raises(NotFoundError):
        client.jobs.get("9999")


@respx.mock
def test_validation_error_exposes_field_errors(client: SMLClient) -> None:
    respx.post("https://api.test.somanylemons.com/api/v1/brands").mock(
        return_value=httpx.Response(
            400,
            json={
                "primary_color": ["Invalid hex color"],
                "detail": "Validation failed",
            },
        )
    )
    with pytest.raises(ValidationError) as exc_info:
        client.brands.create(
            name="Acme",
            primary_color="not-a-color",
            secondary_color="#fff",
        )
    assert "primary_color" in exc_info.value.field_errors


@respx.mock
def test_rate_limit_error_captures_retry_after(client: SMLClient) -> None:
    # Exhaust retries so we actually surface the exception
    client_no_retry = SMLClient(
        api_key="sml_test_key", base_url="https://api.test.somanylemons.com", max_retries=0
    )
    respx.get("https://api.test.somanylemons.com/api/v1/usage").mock(
        return_value=httpx.Response(
            429,
            headers={"Retry-After": "12"},
            json={"detail": "Too many requests"},
        )
    )
    with pytest.raises(RateLimitError) as exc_info:
        client_no_retry.content.get_usage()
    assert exc_info.value.retry_after == 12.0


@respx.mock
def test_quota_error_exposes_usage_fields(client: SMLClient) -> None:
    respx.post("https://api.test.somanylemons.com/api/v1/clip").mock(
        return_value=httpx.Response(
            403,
            json={
                "detail": "render_quota exceeded",
                "renders_used": 5,
                "render_limit": 5,
            },
        )
    )
    with pytest.raises(QuotaError) as exc_info:
        client.reels.create(url="https://example.com/video.mp4")
    assert exc_info.value.renders_used == 5
    assert exc_info.value.render_limit == 5


def test_client_uses_env_key_when_no_arg(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SML_API_KEY", "sml_fromenv12345")
    monkeypatch.setenv("SML_API_URL", "https://env-url.somanylemons.com")
    c = SMLClient()
    assert c._transport._api_key.get() == "sml_fromenv12345"
    assert c.base_url == "https://env-url.somanylemons.com"
    c.close()


def test_client_rejects_missing_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SML_API_KEY", raising=False)
    with pytest.raises(AuthError):
        SMLClient()


def test_reels_create_requires_url_xor_file_path(client: SMLClient) -> None:
    with pytest.raises(ValueError):
        client.reels.create()
    with pytest.raises(ValueError):
        client.reels.create(url="https://a.test", file_path="/tmp/x.mp4")


@respx.mock
def test_reels_create_sends_asset_types(client: SMLClient) -> None:
    route = respx.post("https://api.test.somanylemons.com/api/v1/clip").mock(
        return_value=httpx.Response(
            202,
            json={"id": "abc-123", "status": "pending"},
        )
    )

    client.reels.create(
        url="https://example.com/video.mp4",
        asset_types=["videogram", "image_quote"],
    )

    payload = json.loads(route.calls.last.request.content)
    assert payload["asset_types"] == ["videogram", "image_quote"]


# ── Security tests ──────────────────────────────────────────────────────────

def test_api_key_does_not_leak_via_repr() -> None:
    """`repr(client)` and `repr(transport)` must mask the API key."""
    c = SMLClient(api_key="sml_SuperSecretKey_12345", base_url="https://api.test.somanylemons.com")
    rendered = repr(c) + repr(c._transport)
    assert "sml_SuperSecretKey_12345" not in rendered
    assert "SuperSecret" not in rendered
    assert "redacted" in rendered.lower() or "…" in rendered
    c.close()


def test_api_key_does_not_leak_via_str() -> None:
    from somanylemons.http import _SecretStr

    secret = _SecretStr("sml_SuperSecretKey_12345")
    assert "SuperSecret" not in str(secret)
    assert "SuperSecret" not in repr(secret)
    # Explicit .get() still works for code that needs the raw value
    assert secret.get() == "sml_SuperSecretKey_12345"


def test_rejects_insecure_http_by_default() -> None:
    from somanylemons import SMLError

    with pytest.raises(SMLError, match="plain HTTP"):
        SMLClient(api_key="sml_xxx", base_url="http://api.somanylemons.com")


def test_accepts_insecure_http_with_explicit_opt_in() -> None:
    c = SMLClient(
        api_key="sml_xxx",
        base_url="http://localhost:8000",
        allow_insecure_http=True,
    )
    assert c.base_url == "http://localhost:8000"
    c.close()


def test_rejects_foreign_host_by_default() -> None:
    from somanylemons import SMLError

    with pytest.raises(SMLError, match="not a SoManyLemons domain"):
        SMLClient(api_key="sml_xxx", base_url="https://attacker.example.com")


def test_accepts_foreign_host_with_explicit_opt_in() -> None:
    c = SMLClient(
        api_key="sml_xxx",
        base_url="https://staging.example.com",
        allow_foreign_host=True,
    )
    assert c.base_url == "https://staging.example.com"
    c.close()


def test_api_key_prefix_property_is_masked() -> None:
    c = SMLClient(api_key="sml_AbCdEfGhIj_KlMnOpQrSt", base_url="https://api.somanylemons.com")
    prefix = c.api_key_prefix
    assert "sml_AbCd" in prefix  # first 8 chars visible for identification
    assert "KlMnOp" not in prefix  # later chars hidden
    c.close()


# ── Templates resource ──────────────────────────────────────────────────────

@respx.mock
def test_templates_list_parses_response(client: SMLClient) -> None:
    respx.get("https://api.test.somanylemons.com/api/v1/templates").mock(
        return_value=httpx.Response(
            200,
            json={
                "templates": [
                    {
                        "id": 42,
                        "name": "9:16 Reel",
                        "caption_style": "LEMON",
                        "thumbnail": "/media/thumb.png",
                        "width": 1080,
                        "height": 1920,
                    },
                    {
                        "id": 47,
                        "name": "Square Quote",
                        "caption_style": None,
                        "thumbnail": None,
                        "width": 1080,
                        "height": 1080,
                    },
                ]
            },
        )
    )
    templates = client.templates.list()
    assert len(templates) == 2
    assert templates[0].id == 42
    assert templates[0].name == "9:16 Reel"
    assert templates[1].width == 1080
    assert templates[1].height == 1080


# ── Upload resource ─────────────────────────────────────────────────────────

@respx.mock
def test_upload_file_sends_multipart_and_returns_url(client: SMLClient, tmp_path) -> None:
    test_file = tmp_path / "logo.png"
    test_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)  # minimal PNG-like bytes

    respx.post("https://api.test.somanylemons.com/api/v1/upload").mock(
        return_value=httpx.Response(
            200,
            json={"url": "https://storage.example.com/logos/abc123.png"},
        )
    )
    url = client.upload.upload_file(test_file)
    assert url == "https://storage.example.com/logos/abc123.png"


def test_upload_file_raises_on_missing_file(client: SMLClient) -> None:
    with pytest.raises(FileNotFoundError):
        client.upload.upload_file("/nonexistent/path/file.png")


# ── Client has new resources ────────────────────────────────────────────────

def test_client_exposes_templates_and_upload_resources(client: SMLClient) -> None:
    from somanylemons.resources.templates import TemplatesResource
    from somanylemons.resources.upload import UploadResource

    assert isinstance(client.templates, TemplatesResource)
    assert isinstance(client.upload, UploadResource)
