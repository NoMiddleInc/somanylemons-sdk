# SoManyLemons Python SDK

Typed Python client for the [SoManyLemons Public API](https://api.somanylemons.com/api/v1/docs/). Submit recordings, render branded reels and image quotes, manage brands and drafts — from any Python app, no MCP required.

## Install

```bash
pip install somanylemons
```

## Quickstart

```python
from somanylemons import SMLClient

client = SMLClient(api_key="sml_your_key_here")

# List recent recordings (compact metadata — no URLs)
for job in client.jobs.list(limit=5):
    print(f"{job.id} · {job.title} · {job.clip_count} clips")

# Submit a video and wait for rendered clips
job = client.reels.create_and_wait(
    url="https://example.com/recording.mp4",
    brand_profile_id=1,
    caption_style="LEMON",
    timeout=600,
)
for clip in job.clips:
    print(clip.url)

# Render an image quote with a pinned template (deterministic output)
result = client.image_quotes.create(
    quote_text="Labor productivity is the story of the next five years.",
    brand_profile_id=1,
    template_id=42,
)
print(result.image_url)
```

## Configuration

| Arg / env var | Default | Notes |
|---|---|---|
| `api_key` / `SML_API_KEY` | — (required) | Your `sml_xxx` key |
| `base_url` / `SML_API_URL` | `https://api.somanylemons.com` | Override for QAS / local |
| `timeout` | `30.0` | Seconds per request |
| `max_retries` | `3` | Retries on 5xx and 429 |

```python
client = SMLClient(api_key="sml_xxx", base_url="https://api.qas.somanylemons.com")
```

## Resources

| Attribute | Endpoints |
|---|---|
| `client.jobs` | List, get, poll recordings |
| `client.reels` | Create reels (sync or blocking) |
| `client.transcribe` | Transcribe URL or file |
| `client.image_quotes` | Render branded quote images |
| `client.brands` | Manage brand profiles |
| `client.drafts` | Content queue |
| `client.content` | Generate / score / rewrite posts, extract quotes, usage |

## Error handling

```python
from somanylemons import QuotaError, RateLimitError, JobFailedError, SMLClient

client = SMLClient(api_key="sml_xxx")

try:
    job = client.reels.create_and_wait(url="...")
except QuotaError as exc:
    print(f"Over quota: {exc.renders_used}/{exc.render_limit}")
except RateLimitError as exc:
    print(f"Rate limited, retry after {exc.retry_after}s")
except JobFailedError as exc:
    print(f"Render failed: {exc.message}")
```

## Async

The async client (`AsyncSMLClient`) lands in 0.2.0. For now, wrap sync calls in `asyncio.to_thread`.

## Security

The SDK is built so that common mistakes cannot leak your API key:

- **Keys never appear in `repr` or logs.** The client masks the key in its `__repr__` and stores it in a `_SecretStr` wrapper. Explicit access requires `.get()`.
- **HTTPS enforced by default.** Passing an `http://` URL raises `SMLError` unless you opt in with `allow_insecure_http=True` (e.g. for local dev against `localhost:8000`).
- **Foreign hosts rejected by default.** Your `base_url` must be a SoManyLemons domain. If you need to point at a different host (a staging environment, a proxy), pass `allow_foreign_host=True` so the decision is explicit.
- **Sensible retries only.** 5xx and 429 responses retry with exponential backoff; 4xx errors (auth, permissions, validation) fail fast without retry so bad keys don't hammer the server.

If you're integrating the SDK in a shared / multi-tenant app, create one `SMLClient` per tenant so a per-request key override is never necessary.

## Contributing

The project follows PEP 517/621 so any Python toolchain works (`pip`, `uv`, `poetry`, `rye`, `pixi`). No lockfile is published — consumers use their own.

```bash
# Clone and install in editable mode with dev dependencies
git clone https://github.com/NoMiddleInc/somanylemons-sdk.git
cd somanylemons-sdk
pip install -e ".[dev]"

# Run the test suite (pytest + respx for HTTP mocking)
pytest

# Lint and type-check
ruff check src tests
mypy src
```

Publish flow (maintainers):

```bash
pip install build twine
python -m build
twine upload dist/*
```

## License

MIT
