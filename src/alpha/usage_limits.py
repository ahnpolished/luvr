"""Lightweight v0.1.0 alpha usage limit infrastructure.

Reset policy: counters are designed for a simple monthly reset during the
v0.1.0 alpha. Operators can call ``reset(user_id)`` for the monthly reset or
``reset(user_id, feature=...)`` for a targeted admin correction. This module is
quota bookkeeping only; payment entitlements and billing plans are out of scope.
"""

from __future__ import annotations

from collections.abc import Mapping

from src.alpha.registry import AlphaUserRegistry, UsageLimitResult

DEFAULT_ALPHA_LIMITS: dict[str, int] = {
    "voice_message": 10,
    "tarot_reading": 3,
}


class AlphaUsageLimiter:
    """Feature usage-limit API backed by the minimal alpha user registry."""

    def __init__(
        self,
        registry: AlphaUserRegistry,
        *,
        feature_limits: Mapping[str, int] | None = None,
        reset_policy: str = "monthly",
    ) -> None:
        self._registry = registry
        self._feature_limits = dict(feature_limits or DEFAULT_ALPHA_LIMITS)
        self._reset_policy = reset_policy

    @property
    def reset_policy(self) -> str:
        """Human-readable reset cadence for v0.1.0 alpha counters."""
        return self._reset_policy

    def check_limit(self, user_id: str, feature: str) -> UsageLimitResult:
        """Return whether ``user_id`` can use ``feature`` and remaining quota."""
        limit = self._limit_for(feature)
        self._ensure_known_user(user_id)
        result = self._registry.check_limit(user_id, feature, limit=limit)
        return UsageLimitResult(
            allowed=result.allowed,
            remaining=result.remaining,
            used=result.used,
            limit=result.limit,
            reset_policy=self._reset_policy,
        )

    def increment(self, user_id: str, feature: str) -> UsageLimitResult:
        """Increment usage after successful processing, then return the new state."""
        self._limit_for(feature)
        self._ensure_known_user(user_id)
        self._registry.increment_usage(user_id, feature)
        return self.check_limit(user_id, feature)

    def reset(self, user_id: str, feature: str | None = None) -> None:
        """Reset one feature counter or all counters for the next alpha period."""
        if feature is not None:
            self._limit_for(feature)
        self._ensure_known_user(user_id)
        self._registry.reset_usage(user_id, feature=feature)

    def _limit_for(self, feature: str) -> int:
        try:
            return self._feature_limits[feature]
        except KeyError as error:
            raise KeyError(f"unknown usage-limited feature: {feature}") from error

    def _ensure_known_user(self, user_id: str) -> None:
        try:
            self._registry.get_profile(user_id)
        except KeyError as error:
            raise KeyError(f"unknown alpha user: {user_id}") from error
