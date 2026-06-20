"""Tests for configuration module."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def test_pytest_import_does_not_load_dotenv_secrets(tmp_path):
    """Importing config under pytest must not read a local .env file."""
    secret_token = "dotenv-telegram-token-sentinel"
    (tmp_path / ".env").write_text(
        f"TELEGRAM_BOT_TOKEN={secret_token}\nOPENAI_API_KEY=dotenv-openai-key-sentinel\n",
        encoding="utf-8",
    )

    repo_root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env.update(
        {
            "PYTHONPATH": str(repo_root),
            "PYTEST_CURRENT_TEST": "tests/test_config.py::test_pytest_import_does_not_load_dotenv_secrets (call)",
        }
    )
    for key in ("TELEGRAM_BOT_TOKEN", "OPENAI_API_KEY"):
        env.pop(key, None)

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import json, pytest; from src.config import settings; "
            "print(json.dumps({'telegram_bot_token': settings.telegram_bot_token, "
            "'openai_api_key': settings.openai_api_key}))",
        ],
        cwd=tmp_path,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

    loaded = json.loads(result.stdout)
    assert loaded == {"telegram_bot_token": "", "openai_api_key": None}


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


def test_eval_trace_policy_uses_configured_retention():
    """Test eval trace policy config."""
    from src.config import Settings

    settings = Settings(
        telegram_bot_token="test-token",
        bluebubbles_server_url="http://test:1234",
        eval_trace_retention_days=21,
    )

    assert settings.eval_trace_policy().retention_days == 21
