#!/usr/bin/env python3
"""Smoke test for the Luvr Telegram bot — tests all message types with mocks.

Usage::

    python scripts/telegram_smoke_test.py

Does NOT require:
  - A real Telegram bot token
  - Any API keys (OpenAI, Anthropic, etc.)
  - A running bot instance

All external calls are mocked so the test suite is fast, deterministic,
and safe to run in CI.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Ensure the project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _test_telegram_models():
    """Test that internal message models are importable and work."""
    print("  📦 Testing Telegram models...")
    from src.telegram.models import InternalMessage, TelegramAttachment, TelegramMessageType

    # Create a text message
    msg = InternalMessage(chat_id=123, text="Hello")
    assert msg.chat_id == 123
    assert msg.message_type == TelegramMessageType.TEXT

    # Create a photo message
    att = TelegramAttachment(file_id="f1", mime_type="image/jpeg", file_size=100)
    msg2 = InternalMessage(
        chat_id=456,
        message_type=TelegramMessageType.PHOTO,
        attachment=att,
    )
    assert msg2.message_type == TelegramMessageType.PHOTO
    assert msg2.attachment.file_id == "f1"

    # Create a voice message
    msg3 = InternalMessage(
        chat_id=789,
        message_type=TelegramMessageType.VOICE,
        attachment=TelegramAttachment(file_id="v1", mime_type="audio/ogg"),
    )
    assert msg3.message_type == TelegramMessageType.VOICE

    print("  ✅ Telegram models OK")


def _test_config():
    """Test that Telegram config loads correctly."""
    print("  ⚙️  Testing Telegram config...")
    from src.config import Settings

    s = Settings(
        _env_file=None,
        bluebubbles_server_url="http://test:1234",
        bluebubbles_password="test",
        telegram_bot_token="12345:abc",
        telegram_mode="polling",
    )
    assert s.telegram_bot_token == "12345:abc"
    assert s.telegram_mode == "polling"
    assert s.platform == "imessage"  # default
    print("  ✅ Config OK")


def _test_bridge_client():
    """Test bridge client initialization and cache."""
    print("  🌉 Testing bridge client...")
    from src.telegram.bridge_client import TelegramBridgeClient

    client = TelegramBridgeClient()
    client.cache_attachment("abc", b"data")
    assert client._attachment_cache["abc"] == b"data"

    mock_reply = AsyncMock()
    client.configure(chat_id=123, reply_method=mock_reply)
    assert client._chat_id == 123
    print("  ✅ Bridge client OK")


async def _test_handler_start():
    """Test /start handler."""
    print("  👋 Testing /start handler...")
    from src.telegram.handlers import WELCOME_MESSAGE, handle_start

    msg = MagicMock()
    msg.reply_text = AsyncMock()
    msg.chat_id = 123

    update = MagicMock()
    update.message = msg

    ctx = MagicMock()
    ctx.bot_data = {}

    await handle_start(update, ctx)

    msg.reply_text.assert_called_once_with(WELCOME_MESSAGE)
    print("  ✅ /start OK")


async def _test_handler_text():
    """Test text handler with mock pipeline."""
    print("  💬 Testing text handler...")
    from src.telegram.handlers import handle_text

    msg = MagicMock()
    msg.chat_id = 123
    msg.text = "Should I text him back?"
    msg.reply_text = AsyncMock()

    update = MagicMock()
    update.message = msg

    mock_bc = MagicMock()
    mock_bc.configure = MagicMock()
    mock_bc.send_message = AsyncMock()
    mock_llm = AsyncMock()
    mock_llm.generate_response = AsyncMock(return_value="Test advice")

    with patch("src.handler.text_handler.TextHandler") as MockHandler:
        mock_handler = MagicMock()
        mock_handler._handle_internal = AsyncMock(return_value="Test advice")
        MockHandler.return_value = mock_handler

        await handle_text(update, MagicMock(), bridge_client=mock_bc, llm_client=mock_llm)

    mock_bc.send_message.assert_called_once()
    print("  ✅ Text handler OK")


async def _test_handler_photo():
    """Test photo handler with mock pipeline."""
    print("  📸 Testing photo handler...")
    from src.telegram.handlers import handle_photo

    photo_size = MagicMock()
    photo_size.file_id = "photo_001"
    photo_size.file_size = 50000

    msg = MagicMock()
    msg.chat_id = 123
    msg.photo = [photo_size]
    msg.caption = ""
    msg.reply_text = AsyncMock()

    update = MagicMock()
    update.message = msg

    mock_bc = MagicMock()
    mock_bc.cache_attachment = MagicMock()
    mock_bc.configure = MagicMock()
    mock_bc.send_message = AsyncMock()
    mock_llm = AsyncMock()

    mock_file = MagicMock()
    mock_file.download_as_bytearray = AsyncMock(return_value=bytearray(b"img-data"))

    mock_bot = MagicMock()
    mock_bot.get_file = AsyncMock(return_value=mock_file)

    ctx = MagicMock()
    ctx.bot = mock_bot

    with patch("src.handler.photo_handler.PhotoHandler") as MockHandler:
        mock_handler = MagicMock()
        mock_handler._handle_internal = AsyncMock(return_value="Photo analysis")
        MockHandler.return_value = mock_handler

        await handle_photo(update, ctx, bridge_client=mock_bc, llm_client=mock_llm)

    mock_bc.send_message.assert_called_once()
    print("  ✅ Photo handler OK")


async def _test_handler_voice():
    """Test voice handler with mock pipeline."""
    print("  🎤 Testing voice handler...")
    from src.telegram.handlers import handle_voice

    voice = MagicMock()
    voice.file_id = "voice_001"
    voice.file_size = 30000
    voice.duration = 10
    voice.mime_type = "audio/ogg"

    msg = MagicMock()
    msg.chat_id = 123
    msg.voice = voice
    msg.reply_text = AsyncMock()

    update = MagicMock()
    update.message = msg

    mock_bc = MagicMock()
    mock_bc.cache_attachment = MagicMock()
    mock_bc.configure = MagicMock()
    mock_bc.send_message = AsyncMock()
    mock_llm = AsyncMock()

    mock_file = MagicMock()
    mock_file.download_as_bytearray = AsyncMock(return_value=bytearray(b"voice-data"))

    mock_bot = MagicMock()
    mock_bot.get_file = AsyncMock(return_value=mock_file)

    ctx = MagicMock()
    ctx.bot = mock_bot

    with patch("src.handler.voice_handler.VoiceHandler") as MockHandler:
        mock_handler = MagicMock()
        mock_handler._handle_internal = AsyncMock(return_value="Voice analysis")
        MockHandler.return_value = mock_handler

        await handle_voice(update, ctx, bridge_client=mock_bc, llm_client=mock_llm)

    mock_bc.send_message.assert_called_once()
    print("  ✅ Voice handler OK")


async def _test_handler_error():
    """Test that handler errors are caught gracefully."""
    print("  🛡️  Testing error handling...")
    from src.telegram.handlers import handle_text

    msg = MagicMock()
    msg.chat_id = 123
    msg.text = "test"
    msg.reply_text = AsyncMock()

    update = MagicMock()
    update.message = msg

    mock_bc = MagicMock()
    mock_bc.configure = MagicMock()
    mock_llm = AsyncMock()

    with patch("src.handler.text_handler.TextHandler") as MockHandler:
        mock_handler = MagicMock()
        mock_handler._handle_internal = AsyncMock(side_effect=RuntimeError("Boom"))
        MockHandler.return_value = mock_handler

        await handle_text(update, MagicMock(), bridge_client=mock_bc, llm_client=mock_llm)

    msg.reply_text.assert_called_once()
    assert "Oops" in msg.reply_text.call_args[0][0]
    print("  ✅ Error handling OK")


async def main():
    """Run all smoke tests."""
    print("💨 Luvr Telegram Smoke Tests")
    print("=" * 50)
    print("  (all external APIs are mocked)")
    print()

    try:
        _test_telegram_models()
        _test_config()
        _test_bridge_client()
        await _test_handler_start()
        await _test_handler_text()
        await _test_handler_photo()
        await _test_handler_voice()
        await _test_handler_error()
    except Exception as e:
        print(f"\n❌ Smoke test FAILED: {e}")
        import traceback

        traceback.print_exc()
        return 1

    print("\n" + "=" * 50)
    print("✅ All Telegram smoke tests passed!")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
