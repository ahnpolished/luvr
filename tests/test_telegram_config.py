"""Tests for Telegram configuration extensions."""

from __future__ import annotations

from src.config import Settings


def test_telegram_defaults():
    """Test Telegram config fields have correct defaults."""
    settings = Settings(
        _env_file=None,
        bluebubbles_server_url="http://test:1234",
        bluebubbles_password="test",
    )
    assert settings.telegram_bot_token == ""
    assert settings.telegram_mode == "polling"
    assert settings.telegram_webhook_url is None
    assert settings.telegram_allowed_user_ids == ""


def test_telegram_mode_webhook():
    """Test setting Telegram mode to webhook."""
    settings = Settings(
        _env_file=None,
        bluebubbles_server_url="http://test:1234",
        bluebubbles_password="test",
        telegram_mode="webhook",
        telegram_webhook_url="https://example.com/webhook",
    )
    assert settings.telegram_mode == "webhook"
    assert settings.telegram_webhook_url == "https://example.com/webhook"


def test_platform_default():
    """Test platform field default."""
    settings = Settings(
        _env_file=None,
        bluebubbles_server_url="http://test:1234",
        bluebubbles_password="test",
    )
    assert settings.platform == "imessage"


def test_platform_telegram():
    """Test platform field set to telegram."""
    settings = Settings(
        _env_file=None,
        bluebubbles_server_url="http://test:1234",
        bluebubbles_password="test",
        platform="telegram",
    )
    assert settings.platform == "telegram"


def test_telegram_bot_token_set():
    """Test that Telegram bot token can be set."""
    settings = Settings(
        _env_file=None,
        bluebubbles_server_url="http://test:1234",
        bluebubbles_password="test",
        telegram_bot_token="12345:abcde",
    )
    assert settings.telegram_bot_token == "12345:abcde"


def test_allowed_user_ids_default_empty():
    """Test allowed_user_ids defaults to empty string and parses as empty list."""
    settings = Settings(
        _env_file=None,
        bluebubbles_server_url="http://test:1234",
        bluebubbles_password="test",
    )
    assert settings.telegram_allowed_user_ids == ""
    assert settings.telegram_allowed_user_id_list == []


def test_allowed_user_ids_parsing():
    """Test telegram_allowed_user_id_list parses comma-separated list."""
    settings = Settings(
        _env_file=None,
        bluebubbles_server_url="http://test:1234",
        bluebubbles_password="test",
        telegram_allowed_user_ids="123, 456 , 789",
    )
    assert settings.telegram_allowed_user_id_list == [123, 456, 789]


def test_allowed_user_ids_invalid():
    """Test telegram_allowed_user_id_list with invalid values returns empty list."""
    settings = Settings(
        _env_file=None,
        bluebubbles_server_url="http://test:1234",
        bluebubbles_password="test",
        telegram_allowed_user_ids="abc,def",
    )
    assert settings.telegram_allowed_user_id_list == []


def test_max_attachment_size_20mb():
    """Test updated max attachment size for Telegram (20MB)."""
    settings = Settings(
        _env_file=None,
        bluebubbles_server_url="http://test:1234",
        bluebubbles_password="test",
        max_attachment_size_mb=20,
    )
    assert settings.max_attachment_size_bytes == 20 * 1024 * 1024
