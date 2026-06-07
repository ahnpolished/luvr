"""Shared test fixtures and mocks for Luvr test suite."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

pytest_plugins = []  # allow conftest-level plugin registration


@pytest.fixture
def mock_settings(monkeypatch):
    """Set up mock settings for testing."""
    monkeypatch.setenv("BLUEBUBBLES_SERVER_URL", "http://localhost:1234")
    monkeypatch.setenv("BLUEBUBBLES_PASSWORD", "test_password")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-openai-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-anthropic-key")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("DEBUG", "true")


@pytest.fixture
def sample_text_payload():
    """Sample BlueBubbles webhook payload for a text message."""
    return {
        "chatGuid": "iMessage;-;+1234567890",
        "text": "Should I text him back tonight?",
        "subject": "",
        "sender": "+1234567890",
        "isFromMe": False,
        "attachments": [],
    }


@pytest.fixture
def sample_photo_payload():
    """Sample BlueBubbles webhook payload for a photo message."""
    return {
        "chatGuid": "iMessage;-;+1234567890",
        "text": "What do you think of this profile?",
        "subject": "",
        "sender": "+1234567890",
        "isFromMe": False,
        "attachments": [
            {
                "guid": "attachment-guid-001",
                "mimeType": "image/jpeg",
                "size": 102400,
                "transferState": 1,
            }
        ],
    }


@pytest.fixture
def sample_voice_payload():
    """Sample BlueBubbles webhook payload for a voice memo."""
    return {
        "chatGuid": "iMessage;-;+1234567890",
        "text": "",
        "subject": "",
        "sender": "+1234567890",
        "isFromMe": False,
        "attachments": [
            {
                "guid": "attachment-guid-002",
                "mimeType": "audio/x-caf",
                "size": 51200,
                "transferState": 1,
            }
        ],
    }


@pytest.fixture
def sample_own_message_payload():
    """Sample payload for a message sent by the bot itself."""
    return {
        "chatGuid": "iMessage;-;+1234567890",
        "text": "Here's my advice...",
        "sender": "+1234567890",
        "isFromMe": True,
        "attachments": [],
    }


@pytest.fixture
def mock_bridge_client():
    """Mock BlueBubbles client for handler tests."""
    client = AsyncMock()
    client.send_message = AsyncMock(return_value=MagicMock(status=0, message="ok"))
    client.download_attachment = AsyncMock(return_value=b"fake-binary-data")
    return client


@pytest.fixture
def mock_llm_client():
    """Mock LLM client for handler tests."""
    client = AsyncMock()
    client.generate_response = AsyncMock(return_value="Here's my thoughtful dating advice based on your situation.")
    client.analyze_image = AsyncMock(return_value="Based on the image, here's some advice about this dating profile.")
    return client
