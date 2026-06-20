"""Tarot reading alpha usage limit.

Convenience wrapper so the tarot command handler can check/increment limits
without managing the limiter directly.
"""

from __future__ import annotations

from src.alpha.registry import AlphaUserRegistry, UsageLimitResult
from src.alpha.usage_limits import AlphaUsageLimiter


class TarotUsageGate:
    """Per-user gate for free alpha tarot readings."""

    def __init__(self, registry: AlphaUserRegistry) -> None:
        self._limiter = AlphaUsageLimiter(registry)

    def check(self, user_id: str) -> UsageLimitResult:
        """Return whether this user can request a free tarot reading."""
        return self._limiter.check_limit(user_id, "tarot_reading")

    def increment(self, user_id: str) -> UsageLimitResult:
        """Increment the user's tarot counter after a completed reading."""
        return self._limiter.increment(user_id, "tarot_reading")

    def reset(self, user_id: str) -> None:
        """Admin reset of one user's tarot counter."""
        self._limiter.reset(user_id, feature="tarot_reading")
