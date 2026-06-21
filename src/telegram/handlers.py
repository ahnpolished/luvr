"""Telegram message handler functions.

Each handler receives a ``telegram.Update`` and ``telegram.ext.ContextTypes.DEFAULT_TYPE``,
extracts the relevant data, and dispatches to the existing Luvr handler pipeline.
"""

from __future__ import annotations

import asyncio

import structlog
from telegram.ext import ContextTypes

from src.alpha.registry import AlphaUserRegistry
from src.alpha.tarot_usage import TarotUsageGate
from src.alpha_auth import build_linking_url
from src.handler.split import split_response
from src.llm.client import LLMClient
from src.llm.prompts import PERSONA_DISPLAY_NAMES
from src.llm.tarot import MAJOR_ARCANA, build_tarot_prompt
from src.tarot.images import CARD_SLUGS, card_image_path, random_cards
from src.telegram.bridge_client import TelegramBridgeClient
from src.telegram.models import InternalMessage, TelegramAttachment, TelegramMessageType
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

logger = structlog.get_logger(__name__)

WELCOME_MESSAGE = (
    "💝 Hey there! I'm Luvr, your personal dating advice assistant.\n\n"
    "Send me a text, photo, or voice memo and I'll give you warm, honest advice "
    "on dating, relationships, and communication.\n\n"
    "Use /persona to pick a vibe, or /tarot for a 3-card relationship reading.\n\n"
    "Just text me like you'd text a wise friend!"
)

PERSONA_CALLBACK_PREFIX = "persona:"
PERSONA_RESET_SLUG = "default"

# Card slugs are Major Arcana in canonical order (0-21), matching MAJOR_ARCANA.
CARD_NAME_BY_SLUG: dict[str, str] = dict(zip(CARD_SLUGS, [card["name_en"] for card in MAJOR_ARCANA], strict=True))


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

    # --- Resolve the user's selected persona, if any ---
    persona = _resolve_persona(update, context)

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
        response = await handler._handle_internal(msg, persona=persona)
        if response:
            await _send_bubbles(bc, chat_id, response)
    except Exception:
        logger.exception("text_handler_error")
        await update.message.reply_text("😅 Oops, something went wrong on my end. Could you try again?")


def _resolve_persona(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | None:
    """Look up the requesting user's selected persona, if a profile exists."""
    registry: AlphaUserRegistry | None = context.bot_data.get("alpha_registry")
    if registry is None or update.effective_user is None:
        return None
    profile = registry.find_by_telegram(telegram_user_id=update.effective_user.id)
    if profile is None or profile.persona == PERSONA_RESET_SLUG:
        return None
    return profile.persona


async def _send_bubbles(bc: TelegramBridgeClient, chat_id: int, response: str) -> None:
    """Send a (possibly multi-bubble) LLM response with a natural typing delay."""
    bubbles = split_response(response)
    for i, bubble in enumerate(bubbles):
        if i > 0:
            await asyncio.sleep(settings.multi_turn_delay_seconds)
        await bc.send_message(chat_guid=str(chat_id), message=bubble)


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
            await _send_bubbles(bc, chat_id, response)
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
        await _send_bubbles(bc, chat_id, response)

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


async def handle_link(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    bridge_client: TelegramBridgeClient | None = None,
    llm_client: LLMClient | None = None,
) -> None:
    """Handle the /link command — send a deep-link to web auth/onboarding."""
    if update.message is None:
        return

    chat_id = update.message.chat_id
    from_user = update.message.from_user
    telegram_user_id = from_user.id if from_user else chat_id

    logger.info("link_command", chat_id=chat_id, telegram_user_id=telegram_user_id)

    url = build_linking_url(telegram_user_id=telegram_user_id, telegram_chat_id=chat_id)
    await update.message.reply_text(
        "🔗 Here's your personal onboarding link:\n\n"
        f"{url}\n\n"
        "Open this link on your phone to authenticate and set up your profile. "
        "This link expires in 10 minutes.",
        disable_web_page_preview=True,
    )


async def handle_persona(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /persona command — show an inline keyboard of persona choices."""
    if update.message is None:
        return

    buttons = [
        [InlineKeyboardButton(label, callback_data=f"{PERSONA_CALLBACK_PREFIX}{slug}")]
        for slug, label in PERSONA_DISPLAY_NAMES.items()
    ]
    reset_callback_data = f"{PERSONA_CALLBACK_PREFIX}{PERSONA_RESET_SLUG}"
    buttons.append([InlineKeyboardButton("💝 Luvr (default)", callback_data=reset_callback_data)])

    await update.message.reply_text(
        "Pick a vibe for our chats:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def handle_persona_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle a persona selection button tap."""
    query = update.callback_query
    if query is None or query.data is None or query.from_user is None:
        return

    await query.answer()

    slug = query.data.removeprefix(PERSONA_CALLBACK_PREFIX)
    registry: AlphaUserRegistry | None = context.bot_data.get("alpha_registry")
    if registry is None:
        await query.edit_message_text("😅 I'm still waking up. Try /persona again in a moment!")
        return

    profile = registry.get_or_create_for_telegram(
        telegram_user_id=query.from_user.id,
        telegram_chat_id=query.from_user.id,
        telegram_username=query.from_user.username,
        display_name=query.from_user.full_name,
    )
    registry.update_profile(profile.user_id, persona=slug)

    if slug == PERSONA_RESET_SLUG:
        await query.edit_message_text("💝 Back to classic Luvr — your usual warm, honest advice.")
    else:
        await query.edit_message_text(f"{PERSONA_DISPLAY_NAMES.get(slug, slug)} it is! Send me a message anytime.")


async def handle_tarot(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    bridge_client: TelegramBridgeClient | None = None,
    llm_client: LLMClient | None = None,
) -> None:
    """Handle the /tarot command — draw a 3-card relationship spread and read it."""
    if update.message is None or update.message.from_user is None:
        return

    chat_id = update.message.chat_id
    from_user = update.message.from_user
    logger.info("tarot_command", chat_id=chat_id, telegram_user_id=from_user.id)

    bc = bridge_client or context.bot_data.get("bridge_client")
    lc = llm_client or context.bot_data.get("llm_client")
    registry: AlphaUserRegistry | None = context.bot_data.get("alpha_registry")
    tarot_gate: TarotUsageGate | None = context.bot_data.get("tarot_gate")
    if bc is None or lc is None or registry is None or tarot_gate is None:
        logger.error("tarot_dependencies_missing")
        await update.message.reply_text("😅 I'm still waking up. Try again in a moment!")
        return

    profile = registry.get_or_create_for_telegram(
        telegram_user_id=from_user.id,
        telegram_chat_id=chat_id,
        telegram_username=from_user.username,
        display_name=from_user.full_name,
    )

    limit_check = tarot_gate.check(profile.user_id)
    if not limit_check.allowed:
        await update.message.reply_text(
            "🔮 You've used all your free tarot readings for this month "
            f"({limit_check.used}/{limit_check.limit}). New readings unlock next month!"
        )
        return

    bc.configure(chat_id=chat_id, reply_method=update.message.reply_text, bot=context.bot)

    try:
        slugs = random_cards(3)
        card_names = [CARD_NAME_BY_SLUG[slug] for slug in slugs]
        await update.message.reply_text("🔮 Shuffling the deck...")
        await bc.send_photos(
            [card_image_path(slug) for slug in slugs],
            caption=" • ".join(card_names),
        )

        reading_prompt = build_tarot_prompt(card_names)
        reading = await lc.generate_response(
            user_message="Give me my 3-card relationship tarot reading.",
            system_prompt=reading_prompt,
        )
        await _send_bubbles(bc, chat_id, reading)

        tarot_gate.increment(profile.user_id)
    except Exception:
        logger.exception("tarot_handler_error")
        await update.message.reply_text("I had trouble pulling your cards. Could you try /tarot again? 🔮")
