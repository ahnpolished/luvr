"""Tests for Telegram bridge client."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.telegram.bridge_client import TelegramBridgeClient


@pytest.mark.asyncio
async def test_send_voice_not_configured():
    """Test send_voice raises RuntimeError when bot is not configured."""
    client = TelegramBridgeClient()
    with pytest.raises(RuntimeError, match="not configured with bot"):
        await client.send_voice(b"fake-audio")


@pytest.mark.asyncio
async def test_send_voice():
    """Test sending a voice memo through the bridge client."""
    from unittest.mock import AsyncMock

    client = TelegramBridgeClient()
    mock_bot = AsyncMock()
    mock_reply = AsyncMock()
    client.configure(chat_id=123456, reply_method=mock_reply, bot=mock_bot)

    await client.send_voice(b"fake-opus-audio", caption="Voice reply")

    mock_bot.send_voice.assert_called_once()
    call_kwargs = mock_bot.send_voice.call_args[1]
    assert call_kwargs["chat_id"] == 123456
    assert call_kwargs["caption"] == "Voice reply"


@pytest.mark.asyncio
async def test_send_voice_error_handling():
    """Test that send_voice propagates errors."""
    from unittest.mock import AsyncMock

    client = TelegramBridgeClient()
    mock_bot = AsyncMock()
    mock_bot.send_voice.side_effect = Exception("Telegram API error")
    mock_reply = AsyncMock()
    client.configure(chat_id=123456, reply_method=mock_reply, bot=mock_bot)

    with pytest.raises(Exception, match="Telegram API error"):
        await client.send_voice(b"fake-audio")


@pytest.mark.asyncio
async def test_configure_preserves_existing_bot_when_bot_is_none():
    """Test that configure with bot=None keeps previously set bot."""
    from unittest.mock import AsyncMock

    client = TelegramBridgeClient()
    mock_bot = AsyncMock()
    mock_reply = AsyncMock()

    # First configure with a bot
    client.configure(chat_id=1, reply_method=mock_reply, bot=mock_bot)
    assert client._bot is mock_bot

    # Re-configure without bot — should keep previous bot
    client.configure(chat_id=2, reply_method=mock_reply)
    assert client._bot is mock_bot  # preserved


@pytest.mark.asyncio
async def test_send_voice_without_caption():
    """Test sending voice without a caption."""
    from unittest.mock import AsyncMock

    client = TelegramBridgeClient()
    mock_bot = AsyncMock()
    mock_reply = AsyncMock()
    client.configure(chat_id=123456, reply_method=mock_reply, bot=mock_bot)

    await client.send_voice(b"fake-opus-audio")

    call_kwargs = mock_bot.send_voice.call_args[1]
    assert call_kwargs["caption"] is None


def test_bridge_client_initialization():
    """Test that bridge client initializes with empty state."""
    client = TelegramBridgeClient()
    assert client._chat_id == 0
    assert client._message_reply is None
    assert client._attachment_cache == {}


def test_bridge_client_configure():
    """Test configuring bridge client for a message context."""
    client = TelegramBridgeClient()
    mock_reply = AsyncMock()

    client.configure(chat_id=123456, reply_method=mock_reply)

    assert client._chat_id == 123456
    assert client._message_reply is mock_reply


def test_bridge_client_cache_attachment():
    """Test caching attachment bytes."""
    client = TelegramBridgeClient()
    client.cache_attachment("file_abc", b"test-data")

    assert "file_abc" in client._attachment_cache
    assert client._attachment_cache["file_abc"] == b"test-data"


@pytest.mark.asyncio
async def test_download_attachment_returns_cached():
    """Test download_attachment returns pre-cached data."""
    client = TelegramBridgeClient()
    client.cache_attachment("file_xyz", b"cached-bytes")

    result = await client.download_attachment("file_xyz")
    assert result == b"cached-bytes"


@pytest.mark.asyncio
async def test_download_attachment_missing_raises():
    """Test download_attachment raises KeyError for uncached file_ids."""
    client = TelegramBridgeClient()
    with pytest.raises(KeyError, match="not found in cache"):
        await client.download_attachment("nonexistent")


@pytest.mark.asyncio
async def test_send_message_not_configured():
    """Test send_message raises RuntimeError when not configured."""
    client = TelegramBridgeClient()
    with pytest.raises(RuntimeError, match="not configured"):
        await client.send_message(chat_guid="ignored", message="Hello")


@pytest.mark.asyncio
async def test_send_message():
    """Test sending a message through the bridge client."""
    client = TelegramBridgeClient()
    mock_reply = AsyncMock()
    client.configure(chat_id=123456, reply_method=mock_reply)

    await client.send_message(chat_guid="ignored", message="Hello!")

    mock_reply.assert_called_once_with(text="Hello!")


@pytest.mark.asyncio
async def test_send_message_truncates_long():
    """Test messages over 4096 chars are truncated."""
    client = TelegramBridgeClient()
    mock_reply = AsyncMock()
    client.configure(chat_id=123456, reply_method=mock_reply)

    long_msg = "x" * 5000
    await client.send_message(chat_guid="ignored", message=long_msg)

    sent = mock_reply.call_args[1]["text"]
    assert len(sent) <= 4096
    assert sent.endswith("...")


@pytest.mark.asyncio
async def test_send_message_error_handling():
    """Test that send_message propagate errors."""
    client = TelegramBridgeClient()
    mock_reply = AsyncMock(side_effect=Exception("Telegram API error"))
    client.configure(chat_id=123456, reply_method=mock_reply)

    with pytest.raises(Exception, match="Telegram API error"):
        await client.send_message(chat_guid="ignored", message="Hello")


@pytest.mark.asyncio
async def test_aclose_clears_cache():
    """Test that aclose clears the attachment cache."""
    client = TelegramBridgeClient()
    client.cache_attachment("file_1", b"data1")
    client.cache_attachment("file_2", b"data2")

    await client.aclose()

    assert client._attachment_cache == {}


@pytest.mark.asyncio
async def test_health_check():
    """Test health_check always returns True."""
    client = TelegramBridgeClient()
    assert await client.health_check() is True
