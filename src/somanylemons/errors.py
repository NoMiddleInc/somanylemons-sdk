"""Exception hierarchy for the SoManyLemons SDK.

All SDK errors inherit from ``SMLError``. Catch specific subclasses when you
need to handle a particular failure mode; catch ``SMLError`` for a generic
"something went wrong with SML" handler.
"""

from __future__ import annotations

from typing import Any


class SMLError(Exception):
    """Base class for all SDK errors.

    Attributes:
        message: Human-readable description of the failure.
        status_code: HTTP status code returned by the API, if the error came
            from an HTTP response. ``None`` for client-side errors (bad input,
            timeouts, network failures).
        response_body: Parsed JSON body of the error response, if any.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_body: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.message!r}, status={self.status_code})"


class AuthError(SMLError):
    """401 — invalid or missing API key."""


class PermissionError(SMLError):
    """403 — API key has no permission for this resource or no organization."""


class NotFoundError(SMLError):
    """404 — resource not found (wrong ID, or not owned by this API key)."""


class ValidationError(SMLError):
    """400 — request payload failed server-side validation.

    The ``field_errors`` attribute holds per-field details when the server
    returns them.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = 400,
        response_body: Any = None,
        field_errors: dict[str, list[str]] | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, response_body=response_body)
        self.field_errors: dict[str, list[str]] = field_errors or {}


class RateLimitError(SMLError):
    """429 — rate limit exceeded.

    The ``retry_after`` attribute is the number of seconds the server told us
    to wait before retrying, or ``None`` if the header was absent.
    """

    def __init__(
        self,
        message: str,
        *,
        retry_after: float | None = None,
        response_body: Any = None,
    ) -> None:
        super().__init__(message, status_code=429, response_body=response_body)
        self.retry_after = retry_after


class QuotaError(SMLError):
    """Render quota exceeded for the current billing period.

    Returned as a 402 or 403 with a specific error code from the server.
    ``renders_used`` and ``render_limit`` are populated when the server returns
    them in the error body.
    """

    def __init__(
        self,
        message: str,
        *,
        renders_used: int | None = None,
        render_limit: int | None = None,
        response_body: Any = None,
    ) -> None:
        super().__init__(message, status_code=403, response_body=response_body)
        self.renders_used = renders_used
        self.render_limit = render_limit


class ServerError(SMLError):
    """5xx — the SML backend failed. Usually transient; callers should retry."""


class TimeoutError(SMLError):
    """Client-side timeout waiting for a response or a polling operation."""


class JobFailedError(SMLError):
    """A background job (render, transcription) finished with status=failed.

    Raised by ``.wait_for()`` helpers when the polled job reaches a terminal
    failure state. The ``job`` attribute holds the final job model.
    """

    def __init__(self, message: str, *, job: Any = None) -> None:
        super().__init__(message)
        self.job = job
