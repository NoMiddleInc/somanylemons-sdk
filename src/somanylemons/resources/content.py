"""Content resource: generate / score / rewrite posts, extract quotes."""

from __future__ import annotations

from somanylemons.http import SyncTransport


class ContentResource:
    """Access to /api/v1/write/*, /api/v1/extract-clips, and /api/v1/usage."""

    def __init__(self, transport: SyncTransport) -> None:
        self._t = transport

    def generate_post(self, *, topic: str) -> dict:
        """Generate a LinkedIn post from a topic."""
        return self._t.request("POST", "/api/v1/write/generate", json={"topic": topic})

    def score_post(self, *, post_text: str) -> dict:
        """Score a post for engagement potential (0-100 with feedback)."""
        return self._t.request("POST", "/api/v1/write/score", json={"post_text": post_text})

    def rewrite_post(
        self,
        *,
        post_text: str,
        feedback: list[str] | None = None,
    ) -> dict:
        """Rewrite a post to improve engagement, optionally guided by feedback."""
        payload: dict = {"post_text": post_text}
        if feedback:
            payload["feedback"] = feedback
        return self._t.request("POST", "/api/v1/write/rewrite", json=payload)

    def extract_quotes(self, *, text: str, count: int = 8) -> dict:
        """Extract quotable moments from text (min 20 words). Scored 0-50 each."""
        return self._t.request(
            "POST",
            "/api/v1/extract-clips",
            json={"text": text, "count": count},
        )

    def get_usage(self) -> dict:
        """Return the current billing period usage summary."""
        return self._t.request("GET", "/api/v1/usage")
