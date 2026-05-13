# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.3] - 2026-05-13

### Added
- `client.reels.create()` and `.create_and_wait()` now support multi-asset
  render requests via `asset_types`, including `videogram`, `audiogram`, and
  `image_quote`.
- Added explicit render controls for `template_ids`, `orientation`,
  `source_video_fit`, `speaker_name`, `speaker_title`, and `headshot_url`.
- Added `client.usage.get()` for reading current render quota and billing
  period usage from `GET /api/v1/usage`.
- Job details now parse `assets[]` for all rendered outputs while preserving
  legacy `clips[]` support.
- Template listing now supports `asset_type`, `orientation`, and `size`
  filters, and parses template metadata such as `template_key`, `model`,
  `asset_type`, `size`, `thumbnail_url`, `preview_video_url`, and `source`.

### Fixed
- `QuotaError` now handles nested `detail` payloads returned by the API and
  preserves `renders_used` / `render_limit` when they are provided as nested
  values.
- Multipart uploads now serialize `asset_types` and `template_ids` correctly.

## [0.1.2] - 2026-04-18

### Changed
- Release metadata bump for the Python package.

## [0.1.1] - 2026-04-16

### Added
- `client.templates.list()` — list available video/image templates
  (`GET /api/v1/templates`). Returns typed `Template` models with
  `id`, `name`, `caption_style`, `thumbnail`, `width`, `height`.
- `client.upload.upload_file(path)` — upload a local file (logo,
  headshot, short recording) and get a hosted URL
  (`POST /api/v1/upload`). Raises `FileNotFoundError` if path is invalid.
- `Template` model exported from the top-level package.
- 4 new tests covering templates list, upload file, missing file, and
  resource presence on the client.

## [0.1.0] - 2026-04-15

Initial public release.

### Added
- `SMLClient` sync client with 7 resources: `jobs`, `reels`, `transcribe`,
  `image_quotes`, `brands`, `drafts`, `content`.
- Pydantic v2 models for requests and responses.
- Typed error hierarchy: `SMLError`, `AuthError`, `PermissionError`,
  `NotFoundError`, `ValidationError`, `RateLimitError`, `QuotaError`,
  `ServerError`, `TimeoutError`, `JobFailedError`.
- Auto-retry with exponential backoff on 5xx and 429 responses
  (respects the `Retry-After` header).
- `.create_and_wait()` helpers on `reels` and `transcribe` that submit
  a job and poll to completion in one call.
- Security hardening:
  - API key masked in `repr`, `str`, and logs (wrapped in `_SecretStr`).
  - `base_url` validation: HTTPS enforced by default, only SoManyLemons
    hosts accepted by default. Both can be overridden with explicit
    opt-in flags.
- 16 tests covering functional paths and security invariants.

[Unreleased]: https://github.com/NoMiddleInc/somanylemons-sdk/compare/v0.1.3...HEAD
[0.1.3]: https://github.com/NoMiddleInc/somanylemons-sdk/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/NoMiddleInc/somanylemons-sdk/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/NoMiddleInc/somanylemons-sdk/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/NoMiddleInc/somanylemons-sdk/releases/tag/v0.1.0
