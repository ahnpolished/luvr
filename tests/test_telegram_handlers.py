"""Tests for Telegram handler functions."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram.ext import ContextTypes

from src.telegram.handlers import (
    WELCOME_MESSAGE,
    handle_photo,
    handle_start,
    handle_text,
    handle_voice,
)
from telegram import Chat, Message, PhotoSize, Voice

# ---------------------------------------------------------------------------
# Helper: create a mock Telegram Message with reasonable defaults
# ---------------------------------------------------------------------------


def _mock_message(
    chat_id: int = 123456,
    text: str | None = "Hello!",
    photo: list | None = None,
    voice: MagicMock | None = None,
    caption: str | None = None,
) -> MagicMock:
    msg = MagicMock(spec=Message)
    msg.chat_id = chat_id
    msg.chat = MagicMock(spec=Chat)
    msg.chat.id = chat_id
    msg.text = text
    msg.photo = photo
    msg.voice = voice
    msg.caption = caption
    msg.reply_text = AsyncMock()
    return msg


def _mock_update(message: MagicMock) -> MagicMock:
    update = MagicMock()
    update.message = message
    return update


def _mock_context(bridge_client=None, llm_client=None, bot=None) -> MagicMock:
    ctx = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    ctx.bot_data = {}
    if bridge_client:
        ctx.bot_data["bridge_client"] = bridge_client
    if llm_client:
        ctx.bot_data["llm_client"] = llm_client
    if bot:
        ctx.bot = bot
    return ctx


def _setup_bc_llm():
    """Return a tuple of (mock_bc, mock_llm) with common mocks set up."""
    mock_bc = MagicMock()
    mock_bc.cache_attachment = MagicMock()
    mock_bc.configure = MagicMock()
    mock_bc.send_message = AsyncMock()
    mock_llm = AsyncMock()
    return mock_bc, mock_llm


# ---------------------------------------------------------------------------
# /start command
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_handle_start():
    """Test /start sends welcome message."""
    msg = _mock_message()
    update = _mock_update(msg)

    await handle_start(update, _mock_context())

    msg.reply_text.assert_called_once_with(WELCOME_MESSAGE)


@pytest.mark.asyncio
async def test_handle_start_no_message():
    """Test /start with no message (should be a no-op)."""
    update = MagicMock()
    update.message = None

    await handle_start(update, _mock_context())


# ---------------------------------------------------------------------------
# Text handler
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_handle_text_dispatches_to_text_handler():
    """Test text message is handled by the TextHandler pipeline."""
    msg = _mock_message(text="Should I text him?")
    update = _mock_update(msg)

    mock_bc, mock_llm = _setup_bc_llm()

    # Patch TextHandler at its definition site (where it will be imported from)
    with patch("src.handler.text_handler.TextHandler") as MockHandler:
        mock_handler = MagicMock()
        mock_handler._handle_internal = AsyncMock(return_value="Here's my advice.")
        MockHandler.return_value = mock_handler

        await handle_text(update, _mock_context(), bridge_client=mock_bc, llm_client=mock_llm)

        mock_bc.configure.assert_called_once()
        mock_bc.send_message.assert_called_once_with(chat_guid="123456", message="Here's my advice.")


@pytest.mark.asyncio
async def test_handle_text_no_message():
    """Test with no message should return early."""
    update = MagicMock()
    update.message = None

    await handle_text(update, _mock_context())


@pytest.mark.asyncio
async def test_handle_text_no_text():
    """Test with message but no text should return early."""
    msg = _mock_message(text=None)
    update = _mock_update(msg)

    await handle_text(update, _mock_context())


@pytest.mark.asyncio
async def test_handle_text_missing_deps():
    """Test text handler with missing dependencies sends error message."""
    msg = _mock_message(text="Hello")
    update = _mock_update(msg)

    await handle_text(update, _mock_context())

    msg.reply_text.assert_called_once()
    assert "waking up" in msg.reply_text.call_args[0][0]


@pytest.mark.asyncio
async def test_handle_text_handler_error():
    """Test text handler gracefully handles handler errors."""
    msg = _mock_message(text="Hello")
    update = _mock_update(msg)

    mock_bc, mock_llm = _setup_bc_llm()

    with patch("src.handler.text_handler.TextHandler") as MockHandler:
        mock_handler = MagicMock()
        mock_handler._handle_internal = AsyncMock(side_effect=Exception("Boom"))
        MockHandler.return_value = mock_handler

        await handle_text(update, _mock_context(), bridge_client=mock_bc, llm_client=mock_llm)

        msg.reply_text.assert_called_once()
        assert "Oops" in msg.reply_text.call_args[0][0]


# ---------------------------------------------------------------------------
# Photo handler
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_handle_photo_dispatches_to_photo_handler():
    """Test photo message downloads and dispatches to PhotoHandler."""
    photo_size = MagicMock(spec=PhotoSize)
    photo_size.file_id = "photo_123"
    photo_size.file_size = 50000
    photo_size.file_unique_id = "unique_123"
    photo_size.width = 800
    photo_size.height = 600

    msg = _mock_message(photo=[photo_size])
    update = _mock_update(msg)

    mock_bc, mock_llm = _setup_bc_llm()

    mock_tg_file = MagicMock()
    mock_tg_file.download_as_bytearray = AsyncMock(return_value=bytearray(b"fake-photo-data"))

    mock_bot = MagicMock()
    mock_bot.get_file = AsyncMock(return_value=mock_tg_file)

    ctx = _mock_context(bot=mock_bot)

    with patch("src.handler.photo_handler.PhotoHandler") as MockHandler:
        mock_handler = MagicMock()
        mock_handler._handle_internal = AsyncMock(return_value="Photo analysis here.")
        MockHandler.return_value = mock_handler

        await handle_photo(update, ctx, bridge_client=mock_bc, llm_client=mock_llm)

        mock_bot.get_file.assert_called_once_with("photo_123")
        mock_bc.cache_attachment.assert_called_once()
        mock_bc.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_handle_photo_no_photo():
    """Test with message but no photo returns early."""
    msg = _mock_message(photo=None)
    update = _mock_update(msg)

    await handle_photo(update, _mock_context())


@pytest.mark.asyncio
async def test_handle_photo_too_large():
    """Test that oversized photos are rejected."""
    photo_size = MagicMock(spec=PhotoSize)
    photo_size.file_id = "photo_large"
    photo_size.file_size = 30 * 1024 * 1024  # 30MB

    msg = _mock_message(photo=[photo_size])
    update = _mock_update(msg)

    mock_bc, mock_llm = _setup_bc_llm()

    await handle_photo(update, _mock_context(), bridge_client=mock_bc, llm_client=mock_llm)

    msg.reply_text.assert_called_once()
    assert "large" in msg.reply_text.call_args[0][0].lower()


@pytest.mark.asyncio
async def test_handle_photo_handler_error():
    """Test photo handler internal error is gracefully caught."""
    photo_size = MagicMock(spec=PhotoSize)
    photo_size.file_id = "photo_err2"
    photo_size.file_size = 50000

    msg = _mock_message(photo=[photo_size])
    update = _mock_update(msg)

    mock_bc, mock_llm = _setup_bc_llm()

    mock_tg_file = MagicMock()
    mock_tg_file.download_as_bytearray = AsyncMock(return_value=bytearray(b"photo-data"))

    mock_bot = MagicMock()
    mock_bot.get_file = AsyncMock(return_value=mock_tg_file)

    ctx = _mock_context(bot=mock_bot)

    with patch("src.handler.photo_handler.PhotoHandler") as MockHandler:
        mock_handler = MagicMock()
        mock_handler._handle_internal = AsyncMock(side_effect=RuntimeError("Boom"))
        MockHandler.return_value = mock_handler

        await handle_photo(update, ctx, bridge_client=mock_bc, llm_client=mock_llm)

        msg.reply_text.assert_called_once()
        assert "trouble analyzing" in msg.reply_text.call_args[0][0].lower()


@pytest.mark.asyncio
async def test_handle_photo_download_error():
    """Test photo download error sends graceful message."""
    photo_size = MagicMock(spec=PhotoSize)
    photo_size.file_id = "photo_err"
    photo_size.file_size = 50000

    msg = _mock_message(photo=[photo_size])
    update = _mock_update(msg)

    mock_bc, mock_llm = _setup_bc_llm()

    mock_bot = MagicMock()
    mock_bot.get_file = AsyncMock(side_effect=Exception("Network error"))

    ctx = _mock_context(bot=mock_bot)

    await handle_photo(update, ctx, bridge_client=mock_bc, llm_client=mock_llm)

    msg.reply_text.assert_called_once()
    assert "trouble downloading" in msg.reply_text.call_args[0][0].lower()


@pytest.mark.asyncio
async def test_handle_photo_missing_deps():
    """Test photo handler with missing deps sends error."""
    photo_size = MagicMock(spec=PhotoSize)
    photo_size.file_id = "photo_x"

    msg = _mock_message(photo=[photo_size])
    update = _mock_update(msg)

    await handle_photo(update, _mock_context())

    msg.reply_text.assert_called_once()
    assert "waking up" in msg.reply_text.call_args[0][0]


# ---------------------------------------------------------------------------
# Voice handler
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_handle_voice_dispatches_to_voice_handler():
    """Test voice message downloads and dispatches to VoiceHandler."""
    voice = MagicMock(spec=Voice)
    voice.file_id = "voice_456"
    voice.file_size = 30000
    voice.duration = 15
    voice.mime_type = "audio/ogg"

    msg = _mock_message(voice=voice)
    update = _mock_update(msg)

    mock_bc, mock_llm = _setup_bc_llm()

    mock_tg_file = MagicMock()
    mock_tg_file.download_as_bytearray = AsyncMock(return_value=bytearray(b"fake-voice-data"))

    mock_bot = MagicMock()
    mock_bot.get_file = AsyncMock(return_value=mock_tg_file)

    ctx = _mock_context(bot=mock_bot)

    with patch("src.handler.voice_handler.VoiceHandler") as MockHandler:
        mock_handler = MagicMock()
        mock_handler._handle_internal = AsyncMock(return_value="Voice advice here.")
        MockHandler.return_value = mock_handler

        await handle_voice(update, ctx, bridge_client=mock_bc, llm_client=mock_llm)

        mock_bot.get_file.assert_called_once_with("voice_456")
        mock_bc.cache_attachment.assert_called_once()
        mock_bc.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_handle_voice_no_voice():
    """Test with message but no voice returns early."""
    msg = _mock_message(voice=None)
    update = _mock_update(msg)

    await handle_voice(update, _mock_context())


@pytest.mark.asyncio
async def test_handle_voice_too_large():
    """Test oversized voice memos are rejected."""
    voice = MagicMock(spec=Voice)
    voice.file_id = "voice_big"
    voice.file_size = 30 * 1024 * 1024

    msg = _mock_message(voice=voice)
    update = _mock_update(msg)

    mock_bc, mock_llm = _setup_bc_llm()

    await handle_voice(update, _mock_context(), bridge_client=mock_bc, llm_client=mock_llm)

    msg.reply_text.assert_called_once()
    assert "long" in msg.reply_text.call_args[0][0].lower()


@pytest.mark.asyncio
async def test_handle_voice_download_error():
    """Test voice download error sends graceful message."""
    voice = MagicMock(spec=Voice)
    voice.file_id = "voice_err"
    voice.file_size = 30000
    voice.duration = 10
    voice.mime_type = "audio/ogg"

    msg = _mock_message(voice=voice)
    update = _mock_update(msg)

    mock_bc, mock_llm = _setup_bc_llm()

    mock_bot = MagicMock()
    mock_bot.get_file = AsyncMock(side_effect=Exception("Network error"))

    ctx = _mock_context(bot=mock_bot)

    await handle_voice(update, ctx, bridge_client=mock_bc, llm_client=mock_llm)

    msg.reply_text.assert_called_once()
    assert "trouble downloading" in msg.reply_text.call_args[0][0].lower()


@pytest.mark.asyncio
async def test_handle_voice_missing_deps():
    """Test voice handler with missing deps sends error."""
    voice = MagicMock(spec=Voice)
    voice.file_id = "voice_x"

    msg = _mock_message(voice=voice)
    update = _mock_update(msg)

    await handle_voice(update, _mock_context())

    msg.reply_text.assert_called_once()
    assert "waking up" in msg.reply_text.call_args[0][0]


@pytest.mark.asyncio
async def test_handle_voice_handler_error():
    """Test voice handler error is gracefully handled."""
    voice = MagicMock(spec=Voice)
    voice.file_id = "voice_err"
    voice.file_size = 30000
    voice.duration = 10
    voice.mime_type = "audio/ogg"

    msg = _mock_message(voice=voice)
    update = _mock_update(msg)

    mock_bc, mock_llm = _setup_bc_llm()

    mock_tg_file = MagicMock()
    mock_tg_file.download_as_bytearray = AsyncMock(return_value=bytearray(b"voice-data"))

    mock_bot = MagicMock()
    mock_bot.get_file = AsyncMock(return_value=mock_tg_file)

    ctx = _mock_context(bot=mock_bot)

    with patch("src.handler.voice_handler.VoiceHandler") as MockHandler:
        mock_handler = MagicMock()
        mock_handler._handle_internal = AsyncMock(side_effect=Exception("Boom"))
        MockHandler.return_value = mock_handler

        await handle_voice(update, ctx, bridge_client=mock_bc, llm_client=mock_llm)

        msg.reply_text.assert_called_once()
        assert "trouble processing" in msg.reply_text.call_args[0][0].lower()


@pytest.mark.asyncio
async def test_handle_voice_sends_voice_reply_when_tts_enabled():
    """Test that voice handler sends a TTS voice reply when enabled."""
    voice = MagicMock(spec=Voice)
    voice.file_id = "voice_reply"
    voice.file_size = 30000
    voice.duration = 15
    voice.mime_type = "audio/ogg"

    msg = _mock_message(voice=voice)
    update = _mock_update(msg)

    mock_bc, mock_llm = _setup_bc_llm()

    mock_tg_file = MagicMock()
    mock_tg_file.download_as_bytearray = AsyncMock(return_value=bytearray(b"voice-data"))

    mock_bot = MagicMock()
    mock_bot.get_file = AsyncMock(return_value=mock_tg_file)

    ctx = _mock_context(bot=mock_bot)

    with (
        patch("src.handler.voice_handler.VoiceHandler") as MockHandler,
        patch("src.telegram.handlers.settings") as mock_settings,
        patch("src.media.speech.text_to_speech") as mock_tts,
    ):
        mock_handler = MagicMock()
        mock_handler._handle_internal = AsyncMock(return_value="Here's my advice.")
        MockHandler.return_value = mock_handler

        mock_settings.tts_enabled = True
        mock_settings.max_attachment_size_bytes = 25 * 1024 * 1024
        mock_tts.return_value = b"fake-tts-audio"

        await handle_voice(update, ctx, bridge_client=mock_bc, llm_client=mock_llm)

        # Text reply should be sent
        mock_bc.send_message.assert_called_once_with(chat_guid="123456", message="Here's my advice.")
        # Voice reply should be sent
        mock_bc.send_voice.assert_called_once_with(b"fake-tts-audio", caption="🔊 Voice reply")
        mock_tts.assert_called_once_with("Here's my advice.")


@pytest.mark.asyncio
async def test_handle_voice_skips_voice_reply_when_tts_disabled():
    """Test that voice handler does NOT send voice reply when TTS is disabled."""
    voice = MagicMock(spec=Voice)
    voice.file_id = "voice_nott"
    voice.file_size = 30000
    voice.duration = 15
    voice.mime_type = "audio/ogg"

    msg = _mock_message(voice=voice)
    update = _mock_update(msg)

    mock_bc, mock_llm = _setup_bc_llm()

    mock_tg_file = MagicMock()
    mock_tg_file.download_as_bytearray = AsyncMock(return_value=bytearray(b"voice-data"))

    mock_bot = MagicMock()
    mock_bot.get_file = AsyncMock(return_value=mock_tg_file)

    ctx = _mock_context(bot=mock_bot)

    with (
        patch("src.handler.voice_handler.VoiceHandler") as MockHandler,
        patch("src.telegram.handlers.settings") as mock_settings,
        patch("src.media.speech.text_to_speech") as mock_tts,
    ):
        mock_handler = MagicMock()
        mock_handler._handle_internal = AsyncMock(return_value="Here's my advice.")
        MockHandler.return_value = mock_handler

        mock_settings.tts_enabled = False
        mock_settings.max_attachment_size_bytes = 25 * 1024 * 1024

        await handle_voice(update, ctx, bridge_client=mock_bc, llm_client=mock_llm)

        # Text reply should still be sent
        mock_bc.send_message.assert_called_once_with(chat_guid="123456", message="Here's my advice.")
        # Voice reply should NOT be sent
        mock_bc.send_voice.assert_not_called()
        mock_tts.assert_not_called()


@pytest.mark.asyncio
async def test_handle_voice_tts_failure_is_non_fatal():
    """Test that TTS failure doesn't break the voice handler — text reply still sent."""
    voice = MagicMock(spec=Voice)
    voice.file_id = "voice_ttsfail"
    voice.file_size = 30000
    voice.duration = 15
    voice.mime_type = "audio/ogg"

    msg = _mock_message(voice=voice)
    update = _mock_update(msg)

    mock_bc, mock_llm = _setup_bc_llm()

    mock_tg_file = MagicMock()
    mock_tg_file.download_as_bytearray = AsyncMock(return_value=bytearray(b"voice-data"))

    mock_bot = MagicMock()
    mock_bot.get_file = AsyncMock(return_value=mock_tg_file)

    ctx = _mock_context(bot=mock_bot)

    with (
        patch("src.handler.voice_handler.VoiceHandler") as MockHandler,
        patch("src.telegram.handlers.settings") as mock_settings,
        patch("src.media.speech.text_to_speech") as mock_tts,
    ):
        mock_handler = MagicMock()
        mock_handler._handle_internal = AsyncMock(return_value="Some advice.")
        MockHandler.return_value = mock_handler

        mock_settings.tts_enabled = True
        mock_settings.max_attachment_size_bytes = 25 * 1024 * 1024
        mock_tts.side_effect = RuntimeError("TTS API down")

        # Should NOT raise — TTS failure is non-fatal
        await handle_voice(update, ctx, bridge_client=mock_bc, llm_client=mock_llm)

        # Text reply should still be sent
        mock_bc.send_message.assert_called_once_with(chat_guid="123456", message="Some advice.")
        # Voice reply should NOT be sent (TTS failed)
        mock_bc.send_voice.assert_not_called()


@pytest.mark.asyncio
async def test_handle_voice_no_response_skips_reply():
    """Test that empty response from VoiceHandler results in no reply."""
    voice = MagicMock(spec=Voice)
    voice.file_id = "voice_empty"
    voice.file_size = 30000
    voice.duration = 15
    voice.mime_type = "audio/ogg"

    msg = _mock_message(voice=voice)
    update = _mock_update(msg)

    mock_bc, mock_llm = _setup_bc_llm()

    mock_tg_file = MagicMock()
    mock_tg_file.download_as_bytearray = AsyncMock(return_value=bytearray(b"voice-data"))

    mock_bot = MagicMock()
    mock_bot.get_file = AsyncMock(return_value=mock_tg_file)

    ctx = _mock_context(bot=mock_bot)

    with (
        patch("src.handler.voice_handler.VoiceHandler") as MockHandler,
        patch("src.telegram.handlers.settings") as mock_settings,
        patch("src.media.speech.text_to_speech") as mock_tts,
    ):
        mock_handler = MagicMock()
        mock_handler._handle_internal = AsyncMock(return_value="")
        MockHandler.return_value = mock_handler

        mock_settings.tts_enabled = True
        mock_settings.max_attachment_size_bytes = 25 * 1024 * 1024

        await handle_voice(update, ctx, bridge_client=mock_bc, llm_client=mock_llm)

        # Neither text nor voice should be sent for empty response
        mock_bc.send_message.assert_not_called()
        mock_bc.send_voice.assert_not_called()
        mock_tts.assert_not_called()
