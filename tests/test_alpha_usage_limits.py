"""Tests for lightweight alpha usage limit infrastructure."""

from __future__ import annotations

import pytest

from src.alpha.registry import AlphaUserRegistry
from src.alpha.usage_limits import DEFAULT_ALPHA_LIMITS, AlphaUsageLimiter


def _profile_user_id(tmp_path) -> tuple[AlphaUserRegistry, str]:
    registry = AlphaUserRegistry(storage_path=tmp_path / "alpha-users.json")
    profile = registry.get_or_create_for_telegram(telegram_user_id=123, telegram_chat_id=456)
    return registry, profile.user_id


def test_first_use_reports_full_remaining_quota(tmp_path):
    """First check exposes configured quota without incrementing usage."""
    registry, user_id = _profile_user_id(tmp_path)
    limiter = AlphaUsageLimiter(registry, feature_limits={"voice_message": 2})

    result = limiter.check_limit(user_id, "voice_message")

    assert result.allowed is True
    assert result.remaining == 2
    assert result.used == 0
    assert result.limit == 2
    assert result.reset_policy == "monthly"
    assert registry.get_profile(user_id).usage_counters == {}


def test_increment_only_after_success_tracks_within_limit_and_limit_hit(tmp_path):
    """Successful completion increments usage until the feature limit is hit."""
    registry, user_id = _profile_user_id(tmp_path)
    limiter = AlphaUsageLimiter(registry, feature_limits={"voice_message": 2})

    limiter.increment(user_id, "voice_message")
    within_limit = limiter.check_limit(user_id, "voice_message")
    limiter.increment(user_id, "voice_message")
    limit_hit = limiter.check_limit(user_id, "voice_message")

    assert within_limit.allowed is True
    assert within_limit.remaining == 1
    assert within_limit.used == 1
    assert limit_hit.allowed is False
    assert limit_hit.remaining == 0
    assert limit_hit.used == 2


def test_default_limits_include_voice_and_tarot(tmp_path):
    """Default v0.1.0 limits cover voice messages and tarot readings."""
    registry, user_id = _profile_user_id(tmp_path)
    limiter = AlphaUsageLimiter(registry)

    assert DEFAULT_ALPHA_LIMITS == {"voice_message": 10, "tarot_reading": 3}
    assert limiter.check_limit(user_id, "voice_message").limit == 10
    assert limiter.check_limit(user_id, "tarot_reading").limit == 3


def test_monthly_reset_policy_can_reset_one_feature_or_all_features(tmp_path):
    """Monthly reset clears feature counters for the next alpha period."""
    registry, user_id = _profile_user_id(tmp_path)
    limiter = AlphaUsageLimiter(registry, feature_limits={"voice_message": 2, "tarot_reading": 1})

    limiter.increment(user_id, "voice_message")
    limiter.increment(user_id, "tarot_reading")

    limiter.reset(user_id, feature="voice_message")
    assert limiter.check_limit(user_id, "voice_message").remaining == 2
    assert limiter.check_limit(user_id, "tarot_reading").remaining == 0

    limiter.reset(user_id)
    assert limiter.check_limit(user_id, "tarot_reading").remaining == 1
    assert registry.get_profile(user_id).usage_counters == {}


def test_unknown_user_and_unknown_feature_are_explicit_errors(tmp_path):
    """Callers get clear errors for unknown users or unconfigured features."""
    registry, user_id = _profile_user_id(tmp_path)
    limiter = AlphaUsageLimiter(registry, feature_limits={"voice_message": 2})

    with pytest.raises(KeyError, match="unknown alpha user"):
        limiter.check_limit("missing-user", "voice_message")

    with pytest.raises(KeyError, match="unknown usage-limited feature"):
        limiter.check_limit(user_id, "unknown_feature")
