"""Tests for message handler pipeline."""

from __future__ import annotations

import pytest

from src.bridge.models import WebhookPayload
from src.handler.pipeline import MessagePipeline
from src.handler.router import MessageRouter


def test_router_text_message(sample_text_payload):
    """Test router correctly identifies text messages."""
    router = MessageRouter()
    payload = WebhookPayload.model_validate(sample_text_payload)
    assert router.route(payload) == "text"


def test_router_photo_message(sample_photo_payload):
    """Test router correctly identifies photo messages."""
    router = MessageRouter()
    payload = WebhookPayload.model_validate(sample_photo_payload)
    assert router.route(payload) == "photo"


def test_router_voice_message(sample_voice_payload):
    """Test router correctly identifies voice messages."""
    router = MessageRouter()
    payload = WebhookPayload.model_validate(sample_voice_payload)
    assert router.route(payload) == "voice"


def test_webhook_payload_parsing(sample_text_payload):
    """Test that BlueBubbles webhook payload is parsed correctly."""
    payload = WebhookPayload.model_validate(sample_text_payload)
    assert payload.chat_guid == "iMessage;-;+1234567890"
    assert payload.text == "Should I text him back tonight?"
    assert payload.sender == "+1234567890"
    assert payload.is_from_me is False
    assert payload.message_type == "text"


def test_webhook_payload_photo_detection(sample_photo_payload):
    """Test photo attachment detection."""
    payload = WebhookPayload.model_validate(sample_photo_payload)
    assert payload.has_images is True
    assert payload.has_audio is False
    assert payload.message_type == "photo"


def test_webhook_payload_audio_detection(sample_voice_payload):
    """Test audio attachment detection."""
    payload = WebhookPayload.model_validate(sample_voice_payload)
    assert payload.has_audio is True
    assert payload.has_images is False
    assert payload.message_type == "voice"


@pytest.mark.asyncio
async def test_pipeline_skips_own_messages(
    mock_bridge_client, mock_llm_client, sample_own_message_payload, monkeypatch
):
    """Test pipeline skips messages sent by the bot."""
    # Ensure skip_own_messages is enabled (the .env file may disable it)
    monkeypatch.setattr("src.handler.pipeline.settings.skip_own_messages", True)

    pipeline = MessagePipeline(bridge_client=mock_bridge_client)
    pipeline._llm_client = mock_llm_client

    await pipeline.process(sample_own_message_payload)

    # Should not call send_message or LLM for own messages
    mock_bridge_client.send_message.assert_not_called()
    mock_llm_client.generate_response.assert_not_called()


@pytest.mark.asyncio
async def test_text_handler(mock_bridge_client, mock_llm_client):
    """Test text handler generates and sends response."""
    from src.bridge.models import WebhookPayload
    from src.handler.text_handler import TextHandler

    handler = TextHandler(llm_client=mock_llm_client)
    payload = WebhookPayload.model_validate({
        "chatGuid": "iMessage;-;+1234567890",
        "text": "Should I text him back?",
        "sender": "+1234567890",
        "isFromMe": False,
        "attachments": [],
    })

    response = await handler.handle(payload)
    assert len(response) > 0
    mock_llm_client.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_text_handler_empty_message(mock_llm_client):
    """Test text handler returns greeting for empty messages."""
    from src.bridge.models import WebhookPayload
    from src.handler.text_handler import TextHandler

    handler = TextHandler(llm_client=mock_llm_client)
    payload = WebhookPayload.model_validate({
        "chatGuid": "iMessage;-;+1234567890",
        "text": "",
        "sender": "+1234567890",
        "isFromMe": False,
        "attachments": [],
    })

    response = await handler.handle(payload)
    assert "mind" in response.lower()
    mock_llm_client.generate_response.assert_not_called()
