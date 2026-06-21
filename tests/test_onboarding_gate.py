"""Tests for the Telegram conversational onboarding gate."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from telegram.ext import ContextTypes

from src.alpha.registry import AlphaUserRegistry
from src.telegram.onboarding import (
    ANONYMOUS_WELCOME_TEXT,
    ONBOARDING_ACTION_ANONYMOUS,
    ONBOARDING_ACTION_SETUP,
    ONBOARDING_CALLBACK_PREFIX,
    OnboardingDecision,
    _onboarding_sessions,
    handle_onboarding_callback,
    is_anonymous_session,
    onboarding_gate,
)
from telegram import CallbackQuery, Chat, Message, Update, User

# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clear_sessions() -> None:
    """Reset the in-memory onboarding session state before each test."""
    _onboarding_sessions.clear()


@pytest.fixture
def registry() -> AlphaUserRegistry:
    """Return a fresh in-memory AlphaUserRegistry."""
    return AlphaUserRegistry(storage_path=None)


def _make_update(
    user_id: int = 12345,
    chat_id: int = 67890,
    text: str = "hello",
) -> Update:
    """Build a minimal Telegram Update for testing the onboarding gate."""
    user = User(
        id=user_id,
        is_bot=False,
        first_name="Test",
    )
    chat = Chat(
        id=chat_id,
        type="private",
    )
    message = Message(
        message_id=1,
        date=None,  # type: ignore[arg-type]
        chat=chat,
        from_user=user,
        text=text,
    )
    return Update(update_id=1, message=message)


def _make_context(registry: AlphaUserRegistry | None = None) -> ContextTypes.DEFAULT_TYPE:
    """Build a minimal ContextTypes.DEFAULT_TYPE with bot_data."""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot_data = {}
    if registry is not None:
        context.bot_data["alpha_registry"] = registry
    return context


# ------------------------------------------------------------------
# OnboardingDecision.PROCEED — authenticated user
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_proceed_when_auth_completed(registry: AlphaUserRegistry) -> None:
    """AC-008: Authenticated user proceeds normally."""
    user_id = 12345
    chat_id = 67890

    # Seed an authenticated profile
    registry.get_or_create_for_telegram(
        telegram_user_id=user_id,
        telegram_chat_id=chat_id,
    )
    registry.update_profile(
        registry.find_by_telegram(telegram_user_id=user_id).user_id,  # type: ignore[union-attr]
        auth_completed=True,
        onboarding_completed=True,
    )

    update = _make_update(user_id=user_id, chat_id=chat_id)
    context = _make_context(registry)

    decision = await onboarding_gate(update, context)
    assert decision == OnboardingDecision.PROCEED


# ------------------------------------------------------------------
# OnboardingDecision.PROMPT — first detection of unauthenticated user
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_prompt_when_first_contact_unauthenticated(registry: AlphaUserRegistry) -> None:
    """AC-001: Unauthenticated user gets onboarding prompt on first message."""
    update = _make_update(user_id=111, chat_id=222)
    context = _make_context(registry)

    decision = await onboarding_gate(update, context)
    assert decision == OnboardingDecision.PROMPT


# ------------------------------------------------------------------
# OnboardingDecision.PENDING — link sent, not yet completed
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_pending_when_link_sent_but_not_completed(registry: AlphaUserRegistry) -> None:
    """AC-003: Awaiting completion shows reminder on subsequent messages."""
    user_id = 111
    chat_id = 222

    # First message triggers PROMPT
    update = _make_update(user_id=user_id, chat_id=chat_id)
    context = _make_context(registry)
    decision1 = await onboarding_gate(update, context)
    assert decision1 == OnboardingDecision.PROMPT

    # Simulate the user choosing "set up" — session state becomes link_sent
    _onboarding_sessions[(user_id, chat_id)] = "link_sent"

    # Second message should be PENDING
    update2 = _make_update(user_id=user_id, chat_id=chat_id, text="are you there?")
    decision2 = await onboarding_gate(update2, context)
    assert decision2 == OnboardingDecision.PENDING


# ------------------------------------------------------------------
# OnboardingDecision.JUST_COMPLETED — auth flips to true mid-session
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_just_completed_when_auth_flips_to_true(registry: AlphaUserRegistry) -> None:
    """AC-004: Freshly authenticated user gets welcome-back."""
    user_id = 111
    chat_id = 222

    # Create profile but don't complete auth yet
    profile = registry.get_or_create_for_telegram(
        telegram_user_id=user_id,
        telegram_chat_id=chat_id,
    )

    # First message — unauthenticated
    update1 = _make_update(user_id=user_id, chat_id=chat_id)
    context = _make_context(registry)
    decision1 = await onboarding_gate(update1, context)
    assert decision1 == OnboardingDecision.PROMPT

    # Simulate web onboarding completing (auth_completed + onboarding_completed)
    registry.update_profile(profile.user_id, auth_completed=True, onboarding_completed=True)

    # Next message — should detect the flip
    update2 = _make_update(user_id=user_id, chat_id=chat_id, text="I'm back")
    decision2 = await onboarding_gate(update2, context)
    assert decision2 == OnboardingDecision.JUST_COMPLETED


# ------------------------------------------------------------------
# OnboardingDecision.ANONYMOUS — user declined
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_anonymous_mode_on_subsequent_messages(registry: AlphaUserRegistry) -> None:
    """AC-005, AC-009: Anonymous user gets ANONYMOUS on subsequent messages."""
    user_id = 111
    chat_id = 222

    # Mark session as anonymous
    _onboarding_sessions[(user_id, chat_id)] = "anonymous"

    update = _make_update(user_id=user_id, chat_id=chat_id, text="help me")
    context = _make_context(registry)

    decision = await onboarding_gate(update, context)
    assert decision == OnboardingDecision.ANONYMOUS


# ------------------------------------------------------------------
# Session re-prompt on restart (loss of in-memory state)
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_re_prompt_on_session_loss(registry: AlphaUserRegistry) -> None:
    """AC-010: Lost session state triggers re-prompt."""
    user_id = 999
    chat_id = 888

    # No session state, not authed — should be PROMPT
    update = _make_update(user_id=user_id, chat_id=chat_id)
    context = _make_context(registry)

    decision = await onboarding_gate(update, context)
    assert decision == OnboardingDecision.PROMPT


# ------------------------------------------------------------------
# is_anonymous_session helper
# ------------------------------------------------------------------


def test_is_anonymous_session_true() -> None:
    """is_anonymous_session returns True when session is anonymous."""
    _onboarding_sessions[(1, 2)] = "anonymous"
    assert is_anonymous_session(1, 2) is True


def test_is_anonymous_session_false() -> None:
    """is_anonymous_session returns False for unknown or non-anonymous sessions."""
    assert is_anonymous_session(99, 99) is False
    _onboarding_sessions[(3, 4)] = "link_sent"
    assert is_anonymous_session(3, 4) is False


# ------------------------------------------------------------------
# Onboarding callback handler — "Set up profile" path
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_handle_onboarding_callback_setup(registry: AlphaUserRegistry) -> None:
    """Tapping 'Set up profile' sends the deep-link and sets session to link_sent."""
    user_id = 555
    callback_data = f"{ONBOARDING_CALLBACK_PREFIX}{ONBOARDING_ACTION_SETUP}"

    query = MagicMock(spec=CallbackQuery)
    query.data = callback_data
    query.from_user = User(id=user_id, is_bot=False, first_name="Tester")
    query.answer = AsyncMock()
    query.edit_message_text = AsyncMock()

    update = Update(update_id=2, callback_query=query)
    context = _make_context(registry)

    await handle_onboarding_callback(update, context)

    query.answer.assert_awaited_once()
    query.edit_message_text.assert_awaited_once()
    call_args = query.edit_message_text.call_args[0][0]
    assert "setup link" in call_args.lower()
    assert _onboarding_sessions.get((user_id, user_id)) == "link_sent"


# ------------------------------------------------------------------
# Onboarding callback handler — "Continue anonymously" path
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_handle_onboarding_callback_anonymous(registry: AlphaUserRegistry) -> None:
    """Tapping 'Continue anonymously' sets session to anonymous and sends welcome."""
    user_id = 555
    callback_data = f"{ONBOARDING_CALLBACK_PREFIX}{ONBOARDING_ACTION_ANONYMOUS}"

    query = MagicMock(spec=CallbackQuery)
    query.data = callback_data
    query.from_user = User(id=user_id, is_bot=False, first_name="Tester")
    query.answer = AsyncMock()
    query.edit_message_text = AsyncMock()

    update = Update(update_id=3, callback_query=query)
    context = _make_context(registry)

    await handle_onboarding_callback(update, context)

    query.answer.assert_awaited_once()
    query.edit_message_text.assert_awaited_once()
    call_args = query.edit_message_text.call_args[0][0]
    assert call_args == ANONYMOUS_WELCOME_TEXT
    assert _onboarding_sessions.get((user_id, user_id)) == "anonymous"


# ------------------------------------------------------------------
# Onboarding gate — missing registry (graceful fallback)
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_gate_returns_proceed_when_no_registry() -> None:
    """Onboarding gate returns PROCEED when registry is not in bot_data."""
    update = _make_update()
    context = _make_context(registry=None)  # No registry

    decision = await onboarding_gate(update, context)
    assert decision == OnboardingDecision.PROCEED


# ------------------------------------------------------------------
# Onboarding gate — missing effective_user (edge case)
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_gate_returns_proceed_when_no_effective_user(registry: AlphaUserRegistry) -> None:
    """Onboarding gate returns PROCEED when there's no effective_user."""
    update = MagicMock(spec=Update)
    update.effective_user = None
    context = _make_context(registry)

    decision = await onboarding_gate(update, context)
    assert decision == OnboardingDecision.PROCEED


# ------------------------------------------------------------------
# Already promoted this session → should return PENDING, not re-prompt
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_already_prompted_returns_pending(registry: AlphaUserRegistry) -> None:
    """When session state is 'prompted', subsequent messages return PENDING (not re-prompt)."""
    user_id = 777
    chat_id = 888
    _onboarding_sessions[(user_id, chat_id)] = "prompted"

    update = _make_update(user_id=user_id, chat_id=chat_id, text="hey again")
    context = _make_context(registry)

    decision = await onboarding_gate(update, context)
    assert decision == OnboardingDecision.PENDING
