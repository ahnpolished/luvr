"""Voice-message usage limit helpers for alpha users."""

from __future__ import annotations

from src.alpha.registry import AlphaUserRegistry, UsageLimitResult

VOICE_FEATURE = "voice"


def check_voice_usage_limit(
    registry: AlphaUserRegistry,
    *,
    user_id: str,
) -> UsageLimitResult:
    return registry.check_limit(user_id=user_id, feature=VOICE_FEATURE)


def record_successful_voice_usage(
    registry: AlphaUserRegistry,
    *,
    user_id: str,
) -> UsageLimitResult:
    registry.increment_usage(user_id=user_id, feature=VOICE_FEATURE)
    return registry.check_limit(user_id=user_id, feature=VOICE_FEATURE)


def voice_limit_response(limit: UsageLimitResult) -> str:
    if limit.allowed:
        return f"Voice memo ready. {limit.remaining} voice messages left this month."

    return "You have hit the alpha voice memo limit for this month. Text still works."
