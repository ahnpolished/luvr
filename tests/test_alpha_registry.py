"""Tests for the v0.1.0 alpha user profile registry."""

from __future__ import annotations

from src.alpha.registry import AlphaUserRegistry


def test_get_or_create_maps_telegram_ids_to_stable_user_id(tmp_path):
    """Registry maps Telegram user/chat identifiers to one internal alpha user."""
    registry = AlphaUserRegistry(storage_path=tmp_path / "alpha-users.json")

    profile = registry.get_or_create_for_telegram(
        telegram_user_id=123,
        telegram_chat_id=456,
        telegram_username="first_handle",
        display_name="First User",
    )
    same_profile = registry.get_or_create_for_telegram(
        telegram_user_id=123,
        telegram_chat_id=456,
        telegram_username="updated_handle",
    )

    assert profile.user_id == same_profile.user_id
    assert same_profile.telegram_user_id == 123
    assert same_profile.telegram_chat_id == 456
    assert same_profile.telegram_username == "updated_handle"
    assert same_profile.display_name == "First User"
    assert registry.find_by_telegram(telegram_user_id=123).user_id == profile.user_id
    assert registry.find_by_telegram(telegram_chat_id=456).user_id == profile.user_id


def test_profile_tracks_auth_onboarding_and_optional_fields(tmp_path):
    """Profile updates track auth/linking state and optional intentional fields."""
    registry = AlphaUserRegistry(storage_path=tmp_path / "alpha-users.json")
    unlinked = registry.find_by_telegram(telegram_user_id=999)

    profile = registry.get_or_create_for_telegram(telegram_user_id=123, telegram_chat_id=456)
    updated = registry.update_profile(
        profile.user_id,
        auth_completed=True,
        onboarding_completed=True,
        nickname="H",
        email="h@example.com",
    )

    assert unlinked is None
    assert registry.has_completed_auth(telegram_user_id=999) is False
    assert registry.has_completed_onboarding(telegram_user_id=999) is False
    assert registry.has_completed_auth(telegram_user_id=123) is True
    assert registry.has_completed_onboarding(telegram_user_id=123) is True
    assert updated.nickname == "H"
    assert updated.email == "h@example.com"


def test_allowlisting_and_weave_labels_resolve_from_registry(tmp_path):
    """Registry exposes allowlist state and Weave-safe labels for alpha traces."""
    registry = AlphaUserRegistry(
        storage_path=tmp_path / "alpha-users.json",
        allowlisted_telegram_user_ids={123},
    )
    profile = registry.get_or_create_for_telegram(
        telegram_user_id=123,
        telegram_chat_id=456,
        telegram_username="humphrey",
        display_name="Humphrey Ahn",
    )
    registry.update_profile(profile.user_id, nickname="H", email="h@example.com")

    labels = registry.weave_labels_for_telegram(telegram_user_id=123)

    assert registry.is_allowlisted(telegram_user_id=123) is True
    assert registry.is_allowlisted(telegram_user_id=999) is False
    assert labels == {
        "user_id": profile.user_id,
        "telegram_user_id": "123",
        "telegram_chat_id": "456",
        "telegram_username": "humphrey",
        "display_name": "Humphrey Ahn",
        "nickname": "H",
        "email": "h@example.com",
        "auth_completed": "false",
        "onboarding_completed": "false",
        "allowlisted": "true",
    }
    assert registry.weave_labels_for_telegram(telegram_user_id=999) == {}


def test_usage_counters_instagram_context_and_persistence_without_memory(tmp_path):
    """Usage counters and Instagram context persist without product-memory fields."""
    storage_path = tmp_path / "alpha-users.json"
    registry = AlphaUserRegistry(storage_path=storage_path)
    profile = registry.get_or_create_for_telegram(telegram_user_id=123, telegram_chat_id=456)

    assert registry.check_limit(profile.user_id, "voice_message", limit=2).allowed is True
    assert registry.check_limit(profile.user_id, "voice_message", limit=2).remaining == 2

    registry.increment_usage(profile.user_id, "voice_message")
    registry.increment_usage(profile.user_id, "voice_message")
    registry.update_profile(
        profile.user_id,
        instagram_context_summary="Public profile suggests outdoorsy, playful tone.",
    )

    assert registry.check_limit(profile.user_id, "voice_message", limit=2).allowed is False
    assert registry.check_limit(profile.user_id, "voice_message", limit=2).remaining == 0

    reloaded = AlphaUserRegistry(storage_path=storage_path)
    reloaded_profile = reloaded.get_profile(profile.user_id)

    assert reloaded_profile.instagram_context_summary == "Public profile suggests outdoorsy, playful tone."
    assert reloaded_profile.usage_counters == {"voice_message": 2}
    assert "memory" not in reloaded_profile.model_dump()


def test_update_profile_sets_persona(tmp_path):
    """update_profile can set and change a user's selected persona."""
    registry = AlphaUserRegistry(storage_path=tmp_path / "alpha-users.json")
    profile = registry.get_or_create_for_telegram(telegram_user_id=123, telegram_chat_id=456)
    assert profile.persona is None

    updated = registry.update_profile(profile.user_id, persona="coach")
    assert updated.persona == "coach"

    updated_again = registry.update_profile(profile.user_id, persona="default")
    assert updated_again.persona == "default"
