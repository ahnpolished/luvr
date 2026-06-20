"""Telegram message handler functions.

Each handler receives a ``telegram.Update`` and ``telegram.ext.ContextTypes.DEFAULT_TYPE``,
extracts the relevant data, and dispatches to the existing Luvr handler pipeline.
"""

from __future__ import annotations

import structlog
from telegram.ext import ContextTypes

from src.llm.client import LLMClient
from src.telegram.bridge_client import TelegramBridgeClient
from src.telegram.models import InternalMessage, TelegramAttachment, TelegramMessageType
from telegram import Update

logger = structlog.get_logger(__name__)

WELCOME_MESSAGE = (
    "💝 Hey there! I'm Luvr, your personal dating advice assistant.\n\n"
    "Send me a text, photo, or voice memo and I'll give you warm, honest advice "
    "on dating, relationships, and communication.\n\n"
    "Just text me like you'd text a wise friend!"
)


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command — send a friendly welcome message."""
    if update.message is None:
        return
    logger.info("start_command", chat_id=update.message.chat_id)
    await update.message.reply_text(WELCOME_MESSAGE)


async def handle_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    bridge_client: TelegramBridgeClient | None = None,
    llm_client: LLMClient | None = None,
) -> None:
    """Handle incoming text messages.

    Extracts the text, creates an ``InternalMessage``, and dispatches to the
    ``TextHandler`` from the existing handler pipeline.

    Args:
        update: Telegram Update object.
        context: Telegram callback context.
        bridge_client: Optional pre-configured bridge client. If None, one is
            retrieved from ``context.bot_data``.
        llm_client: Optional pre-configured LLM client.
    """
    if update.message is None or update.message.text is None:
        return

    chat_id = update.message.chat_id
    text = update.message.text.strip()
    logger.info("telegram_text_received", chat_id=chat_id, text_len=len(text))

    # --- Resolve runtime dependencies ---
    bc = bridge_client or context.bot_data.get("bridge_client")
    lc = llm_client or context.bot_data.get("llm_client")
    if bc is None or lc is None:
        logger.error("handler_dependencies_missing")
        await update.message.reply_text("😅 I'm still waking up. Try again in a moment!")
        return

    # --- Build internal message ---
    msg = InternalMessage(
        chat_id=chat_id,
        message_type=TelegramMessageType.TEXT,
        text=text,
    )

    # --- Configure bridge client for this update ---
    bc.configure(chat_id=chat_id, reply_method=update.message.reply_text, bot=context.bot)

    # --- Dispatch to existing TextHandler ---
    from src.handler.text_handler import TextHandler

    handler = TextHandler(llm_client=lc)
    try:
        response = await handler._handle_internal(msg)
        if response:
            await bc.send_message(chat_guid=str(chat_id), message=response)
    except Exception:
        logger.exception("text_handler_error")
        await update.message.reply_text("😅 Oops, something went wrong on my end. Could you try again?")


async def handle_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    bridge_client: TelegramBridgeClient | None = None,
    llm_client: LLMClient | None = None,
) -> None:
    """Handle incoming photo messages.

    Downloads the largest resolution photo from Telegram, wraps it in an
    ``InternalMessage``, and dispatches to the ``PhotoHandler``.

    Args:
        update: Telegram Update object.
        context: Telegram callback context.
        bridge_client: Optional pre-configured bridge client.
        llm_client: Optional pre-configured LLM client.
    """
    if update.message is None or update.message.photo is None:
        return

    chat_id = update.message.chat_id
    logger.info("telegram_photo_received", chat_id=chat_id)

    bc = bridge_client or context.bot_data.get("bridge_client")
    lc = llm_client or context.bot_data.get("llm_client")
    if bc is None or lc is None:
        logger.error("handler_dependencies_missing")
        await update.message.reply_text("😅 I'm still waking up. Try again in a moment!")
        return

    # Get the largest photo (last in the array)
    photo = update.message.photo[-1]

    # Check file size against limit
    if photo.file_size and photo.file_size > settings.max_attachment_size_bytes:
        await update.message.reply_text(
            f"That photo is a bit large (over {settings.max_attachment_size_mb}MB). "
            "Could you send a smaller version? 📸"
        )
        return

    # --- Download photo ---
    try:
        telegram_file = await context.bot.get_file(photo.file_id)
        data = await telegram_file.download_as_bytearray()
        photo_bytes = bytes(data)
    except Exception:
        logger.exception("photo_download_failed")
        await update.message.reply_text("I had trouble downloading that photo. Could you try again? 📸")
        return

    # --- Cache in bridge client ---
    bc.cache_attachment(photo.file_id, photo_bytes)
    bc.configure(chat_id=chat_id, reply_method=update.message.reply_text, bot=context.bot)

    # --- Build internal message ---
    caption = update.message.caption or ""
    attachment = TelegramAttachment(
        file_id=photo.file_id,
        mime_type="image/jpeg",
        file_size=photo.file_size or len(photo_bytes),
        data=photo_bytes,
    )
    msg = InternalMessage(
        chat_id=chat_id,
        message_type=TelegramMessageType.PHOTO,
        text=caption,
        attachment=attachment,
    )

    # --- Dispatch to PhotoHandler ---
    from src.handler.photo_handler import PhotoHandler

    handler = PhotoHandler(bridge_client=bc, llm_client=lc)
    try:
        response = await handler._handle_internal(msg)
        if response:
            await bc.send_message(chat_guid=str(chat_id), message=response)
    except Exception:
        logger.exception("photo_handler_error")
        await update.message.reply_text("I had trouble analyzing that image. Could you try again or describe it? 🧐")


async def handle_voice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    bridge_client: TelegramBridgeClient | None = None,
    llm_client: LLMClient | None = None,
) -> None:
    """Handle incoming voice messages.

    Downloads the voice recording, wraps it in an ``InternalMessage``, and
    dispatches to the ``VoiceHandler`` which transcribes via Whisper then
    generates dating advice.

    Args:
        update: Telegram Update object.
        context: Telegram callback context.
        bridge_client: Optional pre-configured bridge client.
        llm_client: Optional pre-configured LLM client.
    """
    if update.message is None or update.message.voice is None:
        return

    chat_id = update.message.chat_id
    voice = update.message.voice
    logger.info("telegram_voice_received", chat_id=chat_id, duration=voice.duration)

    bc = bridge_client or context.bot_data.get("bridge_client")
    lc = llm_client or context.bot_data.get("llm_client")
    if bc is None or lc is None:
        logger.error("handler_dependencies_missing")
        await update.message.reply_text("😅 I'm still waking up. Try again in a moment!")
        return

    # Check file size
    if voice.file_size and voice.file_size > settings.max_attachment_size_bytes:
        await update.message.reply_text(
            f"That voice memo is a bit long (over {settings.max_attachment_size_mb}MB). "
            "Could you send a shorter one? 🎤"
        )
        return

    # --- Download voice ---
    try:
        telegram_file = await context.bot.get_file(voice.file_id)
        data = await telegram_file.download_as_bytearray()
        voice_bytes = bytes(data)
    except Exception:
        logger.exception("voice_download_failed")
        await update.message.reply_text("I had trouble downloading that voice memo. Could you try again? 🎤")
        return

    # --- Cache in bridge client ---
    bc.cache_attachment(voice.file_id, voice_bytes)
    bc.configure(chat_id=chat_id, reply_method=update.message.reply_text, bot=context.bot)

    # --- Build internal message ---
    attachment = TelegramAttachment(
        file_id=voice.file_id,
        mime_type=voice.mime_type or "audio/ogg",
        file_size=voice.file_size or len(voice_bytes),
        data=voice_bytes,
    )
    msg = InternalMessage(
        chat_id=chat_id,
        message_type=TelegramMessageType.VOICE,
        text="",
        attachment=attachment,
    )

    # --- Dispatch to VoiceHandler ---
    from src.handler.voice_handler import VoiceHandler

    handler = VoiceHandler(bridge_client=bc, llm_client=lc)
    try:
        response = await handler._handle_internal(msg)
        if not response:
            return

        # Always send the text response first (so the user can read if they can't listen)
        await bc.send_message(chat_guid=str(chat_id), message=response)

        # Send a voice reply if TTS is enabled
        if settings.tts_enabled:
            try:
                from src.media.speech import text_to_speech

                voice_bytes = text_to_speech(response)
                # Use a short caption so the user knows it's the voice reply
                await bc.send_voice(voice_bytes, caption="🔊 Voice reply")
            except Exception:
                logger.exception("tts_voice_reply_failed")
                # Non-fatal: the text reply was already sent
    except Exception:
        logger.exception("voice_handler_error")
        await update.message.reply_text("I had trouble processing that voice memo. Could you try again or type it? 🎤")


# Conditional import to avoid circular issues at module level
from src.config import settings  # noqa: E402
