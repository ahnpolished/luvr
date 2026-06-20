"""Instagram public context extraction primitives.

This module intentionally does not scrape Instagram. It normalizes user-provided
public handles/URLs and stores only explicit public context entered during
onboarding.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


def normalize_instagram_handle(value: str) -> str:
    raw = value.strip()
    if not raw:
        raise ValueError("Instagram handle is required")

    if raw.startswith("@"):
        raw = raw[1:]

    if "://" in raw:
        parsed = urlparse(raw)
        if parsed.netloc not in {"instagram.com", "www.instagram.com"}:
            raise ValueError("Instagram URL must be on instagram.com")
        raw = parsed.path.strip("/").split("/", maxsplit=1)[0]

    handle = raw.strip().lower()
    if not handle or any(char.isspace() for char in handle):
        raise ValueError("Instagram handle is invalid")
    if handle in {"p", "reel", "stories", "explore"}:
        raise ValueError("Instagram profile URL is required")

    return handle


@dataclass(frozen=True)
class InstagramPublicContext:
    handle: str
    bio: str | None = None
    recent_public_hint: str | None = None

    def to_onboarding_context(self) -> dict[str, str]:
        context = {"instagram_handle": normalize_instagram_handle(self.handle)}
        if self.bio:
            context["instagram_bio"] = self.bio.strip()[:280]
        if self.recent_public_hint:
            context["instagram_recent_public_hint"] = self.recent_public_hint.strip()[:280]
        return context
