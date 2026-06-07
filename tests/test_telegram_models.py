"""Tests for Telegram internal message models."""

from __future__ import annotations

from src.telegram.models import (
    InternalMessage,
    TelegramAttachment,
    TelegramMessageType,
)


def test_telegram_message_type_values():
    """Test that TelegramMessageType enum has expected values."""
    assert TelegramMessageType.TEXT == "text"
    assert TelegramMessageType.PHOTO == "photo"
    assert TelegramMessageType.VOICE == "voice"
    assert TelegramMessageType.UNKNOWN == "unknown"


def test_internal_message_default():
    """Test InternalMessage defaults."""
    msg = InternalMessage(chat_id=123456)
    assert msg.chat_id == 123456
    assert msg.message_type == TelegramMessageType.TEXT
    assert msg.text == ""
    assert msg.attachment is None


def test_internal_message_text():
    """Test InternalMessage for a text message."""
    msg = InternalMessage(
        chat_id=123456,
        message_type=TelegramMessageType.TEXT,
        text="Should I text him back?",
    )
    assert msg.chat_id == 123456
    assert msg.message_type == "text"
    assert msg.text == "Should I text him back?"


def test_internal_message_photo():
    """Test InternalMessage for a photo message."""
    attachment = TelegramAttachment(
        file_id="file_789",
        mime_type="image/jpeg",
        file_size=102400,
    )
    msg = InternalMessage(
        chat_id=123456,
        message_type=TelegramMessageType.PHOTO,
        text="What do you think?",
        attachment=attachment,
    )
    assert msg.message_type == "photo"
    assert msg.attachment is not None
    assert msg.attachment.file_id == "file_789"
    assert msg.attachment.mime_type == "image/jpeg"
    assert msg.attachment.file_size == 102400


def test_internal_message_voice():
    """Test InternalMessage for a voice message."""
    attachment = TelegramAttachment(
        file_id="voice_001",
        mime_type="audio/ogg",
        file_size=51200,
    )
    msg = InternalMessage(
        chat_id=123456,
        message_type=TelegramMessageType.VOICE,
        attachment=attachment,
    )
    assert msg.message_type == "voice"
    assert msg.attachment is not None
    assert msg.attachment.file_id == "voice_001"
    assert msg.attachment.mime_type == "audio/ogg"
    assert msg.attachment.file_size == 51200


def test_telegram_attachment_defaults():
    """Test TelegramAttachment defaults."""
    att = TelegramAttachment()
    assert att.file_id == ""
    assert att.mime_type == ""
    assert att.file_size == 0
    assert att.data == b""
    assert att.model_dump() == {
        "file_id": "",
        "mime_type": "",
        "file_size": 0,
    }


def test_telegram_attachment_with_data():
    """Test TelegramAttachment with binary data."""
    att = TelegramAttachment(
        file_id="file_abc",
        mime_type="image/png",
        file_size=5000,
        data=b"fake-binary-data",
    )
    assert att.file_id == "file_abc"
    assert att.data == b"fake-binary-data"


def test_telegram_attachment_data_excluded_from_dump():
    """Test that binary data is excluded from model serialization."""
    att = TelegramAttachment(
        file_id="file_abc",
        data=b"some-bytes",
    )
    dumped = att.model_dump()
    assert "data" not in dumped
