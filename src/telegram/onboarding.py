"""Conversational onboarding gate for the Luvr Telegram bot.

Detects unauthenticated users and guides them through profile setup
conversationally, with an anonymous fallback path.
"""

from __future__ import annotations

from enum import Enum, auto

import structlog
from telegram.ext import ContextTypes

from src.alpha.registry import AlphaUserRegistry
from src.alpha_auth import build_linking_url
from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Update

logger = structlog.get_logger(__name__)

# ------------------------------------------------------------------
# Callback prefix for onboarding inline keyboard buttons
# ------------------------------------------------------------------

ONBOARDING_CALLBACK_PREFIX = "onboarding:"
ONBOARDING_ACTION_SETUP = "setup"
ONBOARDING_ACTION_ANONYMOUS = "anonymous"

# ------------------------------------------------------------------
# Onboarding decision enum
# ------------------------------------------------------------------


class OnboardingDecision(Enum):
    """Result of the onboarding gate check for an incoming message."""

    PROCEED = auto()  # Already authenticated — process normally
    PROMPT = auto()  # Unauthenticated, first detection — send prompt
    PENDING = auto()  # Link sent, awaiting web completion — send reminder
    ANONYMOUS = auto()  # User declined — process anonymously
    JUST_COMPLETED = auto()  # Auth just flipped to true — send welcome-back


# ------------------------------------------------------------------
# In-memory session state (resets on bot restart)
# ------------------------------------------------------------------

# Keyed by (telegram_user_id, telegram_chat_id)
# Values: "prompted" | "link_sent" | "anonymous" | "completed"
_onboarding_sessions: dict[tuple[int, int], str] = {}


def _session_key(telegram_user_id: int, telegram_chat_id: int) -> tuple[int, int]:
    return (telegram_user_id, telegram_chat_id)


# ------------------------------------------------------------------
# Onboarding prompt messages
# ------------------------------------------------------------------

ONBOARDING_PROMPT_TEXT = (
    "💝 Hey! I'm Luvr, your personal dating advice assistant.\n\n"
    "Before we dive in — want to set up your profile? "
    "It takes about 2 minutes and I'll be able to give you "
    "much better, more personal advice.\n\n"
    "*What you get with a profile:*\n"
    "• Personalized advice based on your situation\n"
    "• Pick a vibe that matches your style (/persona)\n"
    "• 3 free tarot readings per month (/tarot)"
)

_setup_cb = f"{ONBOARDING_CALLBACK_PREFIX}{ONBOARDING_ACTION_SETUP}"
_anon_cb = f"{ONBOARDING_CALLBACK_PREFIX}{ONBOARDING_ACTION_ANONYMOUS}"
ONBOARDING_KEYBOARD = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("✨ Set up profile", callback_data=_setup_cb)],
        [InlineKeyboardButton("👋 Continue anonymously", callback_data=_anon_cb)],
    ]
)

PENDING_REMINDER_TEXT = (
    "Your setup link is still open! No rush — I'll be here when "
    "you're ready. Want me to resend the link? Just type /link. 💝"
)

ANONYMOUS_WELCOME_TEXT = (
    "No problem! I'll give you my best advice either way. Just know "
    "some features like personalized context and tarot readings need "
    "a profile. If you change your mind, just type /link anytime.\n\n"
    "What's on your mind? 💝"
)

JUST_COMPLETED_TEXT = "You're all set! 💝 Send me anything — texts, photos, voice memos. I'm here for you."

ANONYMOUS_PERSONA_BLOCK_TEXT = "Personas are available once you set up your profile! Want to do that now?"

ANONYMOUS_TAROT_BLOCK_TEXT = (
    "🔮 Tarot readings need a profile — once you're set up, "
    "you'll get 3 free readings per month! Want to set up your profile?"
)

ANONYMOUS_UPSELL_KEYBOARD = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("✨ Set up profile", callback_data=_setup_cb)],
        [InlineKeyboardButton("Not now", callback_data=_anon_cb)],
    ]
)


# ------------------------------------------------------------------
# Core onboarding gate
# ------------------------------------------------------------------


async def onboarding_gate(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> OnboardingDecision:
    """Determine the onboarding action for an incoming message.

    Checks the alpha registry for auth state and the in-memory session
    tracker to avoid re-prompting. Must be called before any message
    processing logic.

    Args:
        update: Telegram Update object.
        context: Telegram callback context.

    Returns:
        An ``OnboardingDecision`` indicating how the message should be handled.
    """
    if update.effective_user is None or update.effective_chat is None:
        return OnboardingDecision.PROCEED

    telegram_user_id: int = update.effective_user.id
    telegram_chat_id: int = update.effective_chat.id

    registry: AlphaUserRegistry | None = context.bot_data.get("alpha_registry")
    if registry is None:
        return OnboardingDecision.PROCEED

    # Check auth state from the registry (source of truth)
    auth_completed = registry.has_completed_auth(telegram_user_id=telegram_user_id)
    onboarding_completed = registry.has_completed_onboarding(telegram_user_id=telegram_user_id)

    key = _session_key(telegram_user_id, telegram_chat_id)
    session_state = _onboarding_sessions.get(key)

    if auth_completed and onboarding_completed:
        if session_state not in ("completed", None):
            # Auth just flipped to true during this session
            _onboarding_sessions[key] = "completed"
            return OnboardingDecision.JUST_COMPLETED
        _onboarding_sessions[key] = "completed"
        return OnboardingDecision.PROCEED

    # Not fully authenticated
    if session_state == "anonymous":
        return OnboardingDecision.ANONYMOUS

    if session_state == "link_sent":
        return OnboardingDecision.PENDING

    if session_state == "prompted":
        # Already prompted this session — don't re-prompt on every message.
        # Still return PROMPT so the handler can decide whether to re-send.
        # For now, act like PENDING (gentle reminder logic).
        return OnboardingDecision.PENDING

    # First detection this session
    _onboarding_sessions[key] = "prompted"
    return OnboardingDecision.PROMPT


# ------------------------------------------------------------------
# Onboarding callback handler (inline keyboard buttons)
# ------------------------------------------------------------------


async def handle_onboarding_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle taps on the onboarding inline keyboard.

    Routes to either the setup (deep-link) path or the anonymous path.
    """
    query = update.callback_query
    if query is None or query.data is None or query.from_user is None:
        return

    await query.answer()

    action = query.data.removeprefix(ONBOARDING_CALLBACK_PREFIX)
    telegram_user_id: int = query.from_user.id

    if action == ONBOARDING_ACTION_SETUP:
        await _handle_onboarding_setup(query, context, telegram_user_id)
    elif action == ONBOARDING_ACTION_ANONYMOUS:
        await _handle_onboarding_anonymous(query, context, telegram_user_id)
    else:
        logger.warning("unknown_onboarding_action", action=action)


async def _handle_onboarding_setup(
    query: CallbackQuery,
    context: ContextTypes.DEFAULT_TYPE,
    telegram_user_id: int,
) -> None:
    """Send the deep-link URL and mark session as 'link_sent'."""
    # In DMs chat_id == user_id. Use user_id as the chat key for simplicity.
    key = _session_key(telegram_user_id, telegram_user_id)
    _onboarding_sessions[key] = "link_sent"

    url = build_linking_url(telegram_user_id=telegram_user_id, telegram_chat_id=telegram_user_id)

    await query.edit_message_text(
        "Awesome! Here's your personal setup link:\n\n"
        f"{url}\n\n"
        "This link expires in 10 minutes. "
        "Open it on your phone to set up your profile, "
        "then come back here and send me a message. I'll be waiting! 💝",
        disable_web_page_preview=True,
    )


async def _handle_onboarding_anonymous(
    query: CallbackQuery,
    context: ContextTypes.DEFAULT_TYPE,
    telegram_user_id: int,
) -> None:
    """Mark session as anonymous and send the anonymous welcome."""
    key = _session_key(telegram_user_id, telegram_user_id)
    _onboarding_sessions[key] = "anonymous"

    await query.edit_message_text(ANONYMOUS_WELCOME_TEXT)


# ------------------------------------------------------------------
# Helper: check if user is anonymous (for feature gating)
# ------------------------------------------------------------------


def is_anonymous_session(telegram_user_id: int, telegram_chat_id: int) -> bool:
    """Return whether the given user/chat combo is in an anonymous session."""
    return _onboarding_sessions.get(_session_key(telegram_user_id, telegram_chat_id)) == "anonymous"
