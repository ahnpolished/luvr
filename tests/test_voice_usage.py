from pathlib import Path

from src.alpha.registry import AlphaUserRegistry
from src.alpha.voice_usage import (
    check_voice_usage_limit,
    record_successful_voice_usage,
    voice_limit_response,
)


def _registry(tmp_path: Path) -> AlphaUserRegistry:
    return AlphaUserRegistry(storage_path=tmp_path / "alpha.json")


def test_voice_usage_limit_allows_until_monthly_quota(tmp_path: Path) -> None:
    registry = _registry(tmp_path)
    profile = registry.get_or_create_for_telegram(telegram_user_id=123, telegram_chat_id=456)

    first_check = check_voice_usage_limit(registry, user_id=profile.user_id)

    assert first_check.allowed
    assert first_check.limit == 10
    assert first_check.used == 0
    assert first_check.remaining == 10


def test_voice_usage_increments_only_after_success(tmp_path: Path) -> None:
    registry = _registry(tmp_path)
    profile = registry.get_or_create_for_telegram(telegram_user_id=123, telegram_chat_id=456)

    for _ in range(10):
        result = record_successful_voice_usage(registry, user_id=profile.user_id)

    assert not result.allowed
    assert result.used == 10
    assert result.remaining == 0

    limit = check_voice_usage_limit(registry, user_id=profile.user_id)
    assert not limit.allowed
    assert limit.used == 10
    assert limit.remaining == 0


def test_voice_limit_response_distinguishes_allowed_and_blocked(tmp_path: Path) -> None:
    registry = _registry(tmp_path)
    profile = registry.get_or_create_for_telegram(telegram_user_id=123, telegram_chat_id=456)

    allowed = check_voice_usage_limit(registry, user_id=profile.user_id)
    assert voice_limit_response(allowed) == "Voice memo ready. 10 voice messages left this month."

    for _ in range(10):
        blocked = record_successful_voice_usage(registry, user_id=profile.user_id)

    assert (
        voice_limit_response(blocked)
        == "You have hit the alpha voice memo limit for this month. Text still works."
    )
    assert (
        voice_limit_response(check_voice_usage_limit(registry, user_id=profile.user_id))
        == "You have hit the alpha voice memo limit for this month. Text still works."
    )
