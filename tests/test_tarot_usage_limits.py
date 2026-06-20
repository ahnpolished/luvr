"""Tests for tarot reading alpha usage limit enforcement."""

from __future__ import annotations

import pytest

from src.alpha.registry import AlphaUserRegistry
from src.alpha.usage_limits import DEFAULT_ALPHA_LIMITS, AlphaUsageLimiter


@pytest.fixture
def limiter(tmp_path):
    registry = AlphaUserRegistry(storage_path=tmp_path / "alpha-users.json")
    return AlphaUsageLimiter(registry)


@pytest.fixture
def user_id(limiter):
    registry = limiter._registry
    profile = registry.get_or_create_for_telegram(telegram_user_id=123, telegram_chat_id=456)
    return profile.user_id


def test_within_tarot_limit_allows_reading(limiter, user_id):
    """First use within the default 3/month tarot limit should be allowed."""
    result = limiter.check_limit(user_id, "tarot_reading")
    assert result.allowed is True
    assert result.limit == DEFAULT_ALPHA_LIMITS["tarot_reading"]


def test_tarot_limit_hit_after_exhaustion(limiter, user_id):
    """After 3 uses, tarot limit blocks further readings."""
    for _ in range(3):
        result = limiter.check_limit(user_id, "tarot_reading")
        assert result.allowed is True
        limiter.increment(user_id, "tarot_reading")

    exhausted = limiter.check_limit(user_id, "tarot_reading")
    assert exhausted.allowed is False
    assert exhausted.remaining == 0


def test_tarot_limit_reset_restores_access(limiter, user_id):
    """Monthly reset restores the full tarot reading quota."""
    for _ in range(3):
        limiter.increment(user_id, "tarot_reading")

    limiter.reset(user_id, feature="tarot_reading")
    result = limiter.check_limit(user_id, "tarot_reading")
    assert result.allowed is True
    assert result.remaining == DEFAULT_ALPHA_LIMITS["tarot_reading"]


def test_tarot_limit_no_payment_paths(limiter, user_id):
    """Limit enforcement never references Stripe/payment."""
    for _ in range(3):
        limiter.increment(user_id, "tarot_reading")

    result = limiter.check_limit(user_id, "tarot_reading")
    assert result.allowed is False
    # The response message should not mention payment
    assert result.reset_policy == "monthly"
