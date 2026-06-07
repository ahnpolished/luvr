"""Tests for configuration module."""

from __future__ import annotations


def test_settings_defaults(monkeypatch):
    """Test that settings load defaults correctly."""
    monkeypatch.setenv("BLUEBUBBLES_SERVER_URL", "http://test:1234")
    monkeypatch.setenv("BLUEBUBBLES_PASSWORD", "test")

    # Reload settings (they're a module-level singleton, so we need to reimport)
    from src.config import Settings

    settings = Settings(
        _env_file=None,  # Don't read .env file in tests
        bluebubbles_server_url="http://test:1234",
        bluebubbles_password="test",
        host="::",
        llm_provider="openai",
        llm_model="gpt-4o-mini",
    )

    assert settings.host == "::"
    assert settings.port == 8000
    assert settings.llm_provider == "openai"
    assert settings.llm_model == "gpt-4o-mini"
    assert settings.max_attachment_size_mb == 25


def test_max_attachment_size_bytes():
    """Test byte conversion for max attachment size."""
    from src.config import Settings

    settings = Settings(
        _env_file=None,
        bluebubbles_server_url="http://test:1234",
        bluebubbles_password="test",
        max_attachment_size_mb=10,
    )

    assert settings.max_attachment_size_bytes == 10 * 1024 * 1024


def test_temp_dir_creation():
    """Test that temp dir property creates directory."""
    from src.config import Settings

    settings = Settings(
        _env_file=None,
        bluebubbles_server_url="http://test:1234",
        bluebubbles_password="test",
    )

    temp_dir = settings.temp_dir
    assert temp_dir.exists()
    assert temp_dir.name == "tmp"
