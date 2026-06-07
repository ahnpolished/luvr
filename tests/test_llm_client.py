"""Tests for LLM client and factory."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from src.llm.client import LLMClient, LLMError, create_llm_client
from src.llm.prompts import (
    DATING_ADVISOR_SYSTEM_PROMPT,
    ERROR_RESPONSE,
    PHOTO_ANALYSIS_PROMPT,
)


def test_create_openai_client(monkeypatch):
    """Test that OpenAI client is created when configured."""
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
    monkeypatch.setenv("BLUEBUBBLES_SERVER_URL", "http://test:1234")
    monkeypatch.setenv("BLUEBUBBLES_PASSWORD", "test")

    # Remove .env file influence
    with patch("src.llm.client.settings"):
        from src.config import settings as s

        with (
            patch.object(s, "openai_api_key", "sk-test-key"),
            patch.object(s, "llm_provider", "openai"),
        ):
            client = create_llm_client(provider="openai")
            assert client is not None
            assert isinstance(client, LLMClient)


def test_create_anthropic_client(monkeypatch):
    """Test that Anthropic client is created when configured."""
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")

    with patch("src.llm.client.settings"):
        from src.config import settings as s

        with (
            patch.object(s, "anthropic_api_key", "sk-ant-test-key"),
            patch.object(s, "llm_provider", "anthropic"),
        ):
            client = create_llm_client(provider="anthropic")
            assert client is not None
            assert isinstance(client, LLMClient)


def test_create_client_missing_api_key():
    """Test that missing API key raises error."""
    with patch("src.llm.client.settings") as mock_settings:
        mock_settings.openai_api_key = None
        mock_settings.llm_provider = "openai"
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            create_llm_client(provider="openai")


def test_create_client_unsupported_provider():
    """Test that unsupported provider raises error."""
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        create_llm_client(provider="unsupported")  # type: ignore[arg-type]


def test_system_prompt_contains_key_elements():
    """Test that the system prompt includes all required personality traits."""
    assert "empathetic" in DATING_ADVISOR_SYSTEM_PROMPT.lower()
    assert "honest" in DATING_ADVISOR_SYSTEM_PROMPT.lower()
    assert "non-judgmental" in DATING_ADVISOR_SYSTEM_PROMPT.lower()
    assert "practical" in DATING_ADVISOR_SYSTEM_PROMPT.lower()
    assert "safety" in DATING_ADVISOR_SYSTEM_PROMPT.lower()


def test_photo_analysis_prompt():
    """Test photo analysis prompt covers key scenarios."""
    assert "screenshot" in PHOTO_ANALYSIS_PROMPT.lower()
    assert "dating app" in PHOTO_ANALYSIS_PROMPT.lower()
