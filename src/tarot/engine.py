"""Tarot reading session state machine.

Platform-agnostic — the Telegram Mini App is a thin shell.
Reuses existing Luvr LLM providers (via src.llm.client.create_llm_client)
and card image infrastructure (src.tarot.images).
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Literal

from src.tarot.images import MAJOR_ARCANA_SLUGS
from src.tarot.persona import (
    PERSONA_PREAMBLE,
    reader_adapt_message,
    reader_deepen_message,
    reader_interpret_message,
    ritualist_message,
    weaver_message,
)
from src.tarot.positions import RELATIONSHIP_SPREAD

# ------------------------------------------------------------------
# Data models
# ------------------------------------------------------------------

Phase = Literal["ritual", "reveal", "reflect"]


@dataclass
class Card:
    slug: str
    name: str
    arcana: Literal["major", "minor"]
    suit: str | None
    is_reversed: bool
    position_meaning: str
    numeral: str = ""
    glyph: str = ""


@dataclass
class Message:
    speaker: Literal["reader", "user"]
    text: str
    context: str | None = None


@dataclass
class Session:
    id: str
    phase: Phase = "ritual"
    intention: str | None = None
    drawn_cards: list[Card] = field(default_factory=list)
    current_card_index: int | None = None
    dialogue: list[Message] = field(default_factory=list)
    deepened_on: set[int] = field(default_factory=set)
    synthesis: str | None = None
    takeaway: str | None = None
    created_at: float = 0.0
    expires_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()
        if not self.expires_at:
            self.expires_at = self.created_at + 86400  # 24h TTL


# ------------------------------------------------------------------
# Fallback card meanings (used when LLM is unavailable)
# ------------------------------------------------------------------
# fmt: off
# ruff: noqa: E501

FALLBACK_MEANINGS: dict[str, dict[str, str]] = {
    "fool": {
        "upright": "A new beginning — the blank page before the story is written. You're being asked to take a leap of faith, even if you can't see the landing.",
        "reversed": "The leap feels more like a stumble right now. You might be overthinking the first step or running from the last one.",
    },
    "magician": {
        "upright": "You have more tools at your disposal than you realize. The Magician is about willpower — what you focus on, you can manifest.",
        "reversed": "There's a disconnect between what you know you can do and what you're actually doing. The power is there, but it's misdirected.",
    },
    "high_priestess": {
        "upright": "Trust what you know without knowing how you know it. Something beneath the surface is guiding you — listen to that quiet voice.",
        "reversed": "You've been ignoring your intuition in favor of what seems logical. The answers aren't in the spreadsheet — they're in the pause.",
    },
    "lovers": {
        "upright": "Not fate, not a soulmate verdict — this is the card of a real choice. It asks whether you're choosing from desire, or from the fear of being alone.",
        "reversed": "A choice you've been avoiding continues to tug at you. The tension won't resolve until you name what you want.",
    },
    "star": {
        "upright": "After a long stretch of doubt, quiet faith is returning. You're further along in healing than you've been giving yourself credit for.",
        "reversed": "Hope feels far away. But the Star reversed still shines — you might just be looking in the wrong direction for it.",
    },
    "moon": {
        "upright": "The stories we tell ourselves at two in the morning. Confusion and intuition are tangled up — trust what flickers beneath the surface.",
        "reversed": "The fog is lifting. What felt unreadable is getting clearer. You already know more than you've let yourself admit.",
    },
    "sun": {
        "upright": "Clarity. Joy. The warmth after a cold stretch. Whatever was murky is illuminated now — enjoy it without needing to explain it.",
        "reversed": "The light is there but you're shading your eyes. Something good is trying to reach you — let it in.",
    },
    "tower": {
        "upright": "Something needs to fall for something truer to stand. The Tower clears what you wouldn't clear yourself — it feels like loss but it's liberation.",
        "reversed": "You're holding up a structure that's already cracking. The collapse is coming either way — better to let it go on your own terms.",
    },
    "death": {
        "upright": "Not literal death — the end of a cycle. Something that has run its course is being released so something new can grow in its place.",
        "reversed": "You're gripping what's already gone. The longer you resist the ending, the more it hurts. Let the exhale come.",
    },
    "devil": {
        "upright": "Something has a hold on you that you're pretending is fine. Not judgment — just recognition. What pattern keeps pulling you back?",
        "reversed": "The chain is loosening. You can see the pattern now from the outside. The door was never actually locked.",
    },
}
# fmt: on


def _card_name(slug: str) -> str:
    """Convert slug to display name."""
    return slug.replace("_", " ").title()


def _card_numeral(slug: str) -> str:
    """Return Roman numeral for Major Arcana slugs."""
    numerals = {
        "fool": "0",
        "magician": "I",
        "high_priestess": "II",
        "empress": "III",
        "emperor": "IV",
        "hierophant": "V",
        "lovers": "VI",
        "chariot": "VII",
        "strength": "VIII",
        "hermit": "IX",
        "wheel_of_fortune": "X",
        "justice": "XI",
        "hanged_man": "XII",
        "death": "XIII",
        "temperance": "XIV",
        "devil": "XV",
        "tower": "XVI",
        "star": "XVII",
        "moon": "XVIII",
        "sun": "XIX",
        "judgement": "XX",
        "world": "XXI",
    }
    return numerals.get(slug, "")


def _card_glyph(slug: str) -> str:
    """Return astrological/unicode glyph for Major Arcana (aesthetic)."""
    glyphs: dict[str, str] = {
        "fool": "\u2648",
        "magician": "\u263f",
        "high_priestess": "\u263d",
        "lovers": "\u264a",
        "star": "\u2652",
        "moon": "\u2653",
        "sun": "\u2609",
        "wheel_of_fortune": "\u264d",
        "death": "\u264f",
        "world": "\u2641",
    }
    return glyphs.get(slug, "\u2606")


# ------------------------------------------------------------------
# Session store (in-memory, replace with DB/KV for production)
# ------------------------------------------------------------------

_sessions: dict[str, Session] = {}


def create_session() -> Session:
    """Create a new tarot reading session."""
    import uuid

    session = Session(id=str(uuid.uuid4()))
    _sessions[session.id] = session
    return session


def get_session(session_id: str) -> Session | None:
    """Get an existing session, checking TTL."""
    session = _sessions.get(session_id)
    if session and time.time() > session.expires_at:
        del _sessions[session_id]
        return None
    return session


# ------------------------------------------------------------------
# LLM helper
# ------------------------------------------------------------------


async def _llm_complete(user_message: str, system_prompt: str | None = None) -> str:
    """Run an LLM completion using the existing Luvr provider."""
    from src.llm.client import create_llm_client

    client = create_llm_client()
    return await client.generate_response(
        user_message=user_message,
        system_prompt=system_prompt,
    )


# ------------------------------------------------------------------
# Card logic
# ------------------------------------------------------------------


def draw_cards(count: int = 3) -> list[Card]:
    """Draw n random Major Arcana cards (server-side randomness)."""
    slugs = random.sample(MAJOR_ARCANA_SLUGS, min(count, len(MAJOR_ARCANA_SLUGS)))

    cards: list[Card] = []
    for i, slug in enumerate(slugs):
        is_rev = random.random() < 0.3  # 30% chance of reversal
        position = RELATIONSHIP_SPREAD[i] if i < len(RELATIONSHIP_SPREAD) else RELATIONSHIP_SPREAD[0]
        cards.append(
            Card(
                slug=slug,
                name=_card_name(slug),
                arcana="major",
                suit=None,
                is_reversed=is_rev,
                position_meaning=position.title,
                numeral=_card_numeral(slug),
                glyph=_card_glyph(slug),
            )
        )
    return cards


def get_fallback_meaning(card: Card) -> str:
    """Get a fallback card meaning when LLM is unavailable."""
    meanings = FALLBACK_MEANINGS.get(card.slug)
    if meanings:
        return meanings["reversed"] if card.is_reversed else meanings["upright"]
    reversal_note = " (reversed)" if card.is_reversed else ""
    return (
        f"The {card.name}{reversal_note} appears in the position of "
        f"{card.position_meaning}. This card invites reflection on this area of your life."
    )


# ------------------------------------------------------------------
# LLM calls for each step
# ------------------------------------------------------------------


async def _run_ritualist(intention: str) -> str:
    """Mirror the user's intention in the tarot persona voice."""
    try:
        return await _llm_complete(
            user_message=ritualist_message(intention),
            system_prompt=PERSONA_PREAMBLE,
        )
    except Exception:
        return f"So you're asking about {intention.lower()} — let's see what the cards have to say."


async def _run_reader_interpret(session: Session, card_index: int) -> str:
    """Interpret a single card in its position."""
    card = session.drawn_cards[card_index]
    reversed_status = "reversed" if card.is_reversed else "upright"
    dialogue_summary = "\n".join(f"{m.speaker}: {m.text}" for m in session.dialogue[-6:]) or "(no dialogue yet)"

    try:
        return await _llm_complete(
            user_message=reader_interpret_message(
                intention=session.intention or "a relationship question",
                card_name=card.name,
                card_position=card.position_meaning,
                reversed_status=reversed_status,
                numeral=card.numeral,
                dialogue_summary=dialogue_summary,
            ),
            system_prompt=PERSONA_PREAMBLE,
        )
    except Exception:
        return get_fallback_meaning(card)


async def _run_reader_deepen(session: Session, card_index: int) -> str:
    """Go deeper on a specific card."""
    card = session.drawn_cards[card_index]
    reversed_status = "reversed" if card.is_reversed else "upright"
    dialogue_summary = "\n".join(f"{m.speaker}: {m.text}" for m in session.dialogue[-8:]) or "(no dialogue yet)"

    last_interp = next(
        (
            m.text
            for m in reversed(session.dialogue)
            if m.speaker == "reader" and m.context and m.context.startswith(f"card_{card_index}")
        ),
        get_fallback_meaning(card),
    )

    try:
        return await _llm_complete(
            user_message=reader_deepen_message(
                intention=session.intention or "a relationship question",
                card_name=card.name,
                card_position=card.position_meaning,
                reversed_status=reversed_status,
                dialogue_summary=dialogue_summary,
                last_interpretation=last_interp,
            ),
            system_prompt=PERSONA_PREAMBLE,
        )
    except Exception:
        return (
            f"Let's sit with the {card.name} a moment longer. "
            "What these symbols stir in you is as important as anything I could say."
        )


async def _run_reader_adapt(session: Session, card_index: int, correction: str) -> str:
    """Adapt an interpretation based on user correction."""
    card = session.drawn_cards[card_index]
    reversed_status = "reversed" if card.is_reversed else "upright"
    dialogue_summary = "\n".join(f"{m.speaker}: {m.text}" for m in session.dialogue[-8:]) or "(no dialogue yet)"

    last_interp = next(
        (
            m.text
            for m in reversed(session.dialogue)
            if m.speaker == "reader" and m.context and m.context.startswith(f"card_{card_index}")
        ),
        get_fallback_meaning(card),
    )

    try:
        return await _llm_complete(
            user_message=reader_adapt_message(
                intention=session.intention or "a relationship question",
                card_name=card.name,
                card_position=card.position_meaning,
                reversed_status=reversed_status,
                dialogue_summary=dialogue_summary,
                last_interpretation=last_interp,
                correction=correction,
            ),
            system_prompt=PERSONA_PREAMBLE,
        )
    except Exception:
        return (
            f"I hear you. Let me reframe — the {card.name} isn't about judgment, "
            "it's about awareness. Take what fits and leave the rest."
        )


async def _run_weaver(session: Session) -> tuple[str, str]:
    """Weave all cards into a synthesis narrative + takeaway."""
    cards_summary = "\n".join(
        f"- {c.name} ({'reversed' if c.is_reversed else 'upright'}) in {c.position_meaning}"
        for c in session.drawn_cards
    )
    dialogue_summary = "\n".join(f"{m.speaker}: {m.text}" for m in session.dialogue) or "(no dialogue)"

    try:
        response = await _llm_complete(
            user_message=weaver_message(
                intention=session.intention or "a relationship question",
                cards_summary=cards_summary,
                dialogue_summary=dialogue_summary,
            ),
            system_prompt=PERSONA_PREAMBLE,
        )

        if "## Takeaway" in response:
            parts = response.split("## Takeaway", 1)
            synthesis = parts[0].strip()
            takeaway = parts[1].strip()
        else:
            synthesis = response.strip()
            sentences = synthesis.rsplit(". ", 1)
            takeaway = sentences[1].rstrip(".") if len(sentences) > 1 else "Trust what the cards have shown you."
        return synthesis, takeaway
    except Exception:
        cards_list = ", ".join(c.name for c in session.drawn_cards)
        return (
            f"The {cards_list} have spoken to your question about {session.intention or 'your situation'}. "
            "Each card brought its own wisdom — take what resonates and sit with it.",
            "Trust what the cards have shown you.",
        )


# ------------------------------------------------------------------
# State machine
# ------------------------------------------------------------------


async def advance_session(session: Session, action: dict) -> dict:
    """Advance a session with a user action. Returns a UI instruction dict."""

    kind = action.get("kind", "")

    if kind == "set_intention":
        text = (action.get("text", "") or "").strip()
        if not text:
            return {"error": "intention is required"}

        session.intention = text
        session.dialogue.append(Message(speaker="user", text=text, context="intention"))

        mirror = await _run_ritualist(text)
        session.dialogue.append(Message(speaker="reader", text=mirror, context="intention_mirror"))

        return {
            "session_id": session.id,
            "phase": session.phase,
            "messages": _serialize_messages(session.dialogue[-2:]),
        }

    elif kind == "draw_cards":
        session.drawn_cards = draw_cards(count=3)
        session.phase = "reveal"
        session.current_card_index = 0

        first_interpretation = await _run_reader_interpret(session, 0)
        session.dialogue.append(
            Message(
                speaker="reader",
                text=first_interpretation,
                context="card_0_initial",
            )
        )

        return {
            "session_id": session.id,
            "phase": session.phase,
            "cards": _serialize_cards(session.drawn_cards),
            "messages": _serialize_messages(session.dialogue[-1:]),
        }

    elif kind == "respond":
        card_index = action.get("card_index", session.current_card_index or 0)
        response = action.get("response", "resonates")

        if response == "tell_me_more":
            session.deepened_on.add(card_index)
            deeper = await _run_reader_deepen(session, card_index)
            session.dialogue.append(
                Message(
                    speaker="reader",
                    text=deeper,
                    context=f"card_{card_index}_deepen",
                )
            )
        elif response == "not_quite":
            correction = action.get("correction_text", "")
            if correction:
                session.dialogue.append(
                    Message(
                        speaker="user",
                        text=correction,
                        context=f"card_{card_index}_correction",
                    )
                )
            adapted = await _run_reader_adapt(session, card_index, correction)
            session.dialogue.append(
                Message(
                    speaker="reader",
                    text=adapted,
                    context=f"card_{card_index}_adapted",
                )
            )

        return {
            "session_id": session.id,
            "phase": session.phase,
            "messages": _serialize_messages(session.dialogue[-3:]),
        }

    elif kind == "continue":
        next_index = (session.current_card_index or 0) + 1

        if next_index >= len(session.drawn_cards):
            # All cards done — weave synthesis
            session.phase = "reflect"
            synthesis, takeaway = await _run_weaver(session)
            session.synthesis = synthesis
            session.takeaway = takeaway
            session.dialogue.append(
                Message(
                    speaker="reader",
                    text=synthesis,
                    context="synth",
                )
            )
            session.dialogue.append(
                Message(
                    speaker="reader",
                    text=takeaway,
                    context="takeaway",
                )
            )
            return {
                "session_id": session.id,
                "phase": session.phase,
                "messages": _serialize_messages(session.dialogue[-2:]),
            }

        # Next card
        session.current_card_index = next_index
        interpretation = await _run_reader_interpret(session, next_index)
        session.dialogue.append(
            Message(
                speaker="reader",
                text=interpretation,
                context=f"card_{next_index}_initial",
            )
        )

        return {
            "session_id": session.id,
            "phase": session.phase,
            "current_card_index": next_index,
            "messages": _serialize_messages(session.dialogue[-1:]),
        }

    else:
        return {"error": f"unknown action kind: {kind}"}


# ------------------------------------------------------------------
# Serialization helpers
# ------------------------------------------------------------------


def _serialize_cards(cards: list[Card]) -> list[dict]:
    return [
        {
            "slug": c.slug,
            "name": c.name,
            "arcana": c.arcana,
            "suit": c.suit,
            "is_reversed": c.is_reversed,
            "position_meaning": c.position_meaning,
            "numeral": c.numeral,
            "glyph": c.glyph,
        }
        for c in cards
    ]


def _serialize_messages(messages: list[Message]) -> list[dict]:
    return [{"speaker": m.speaker, "text": m.text, "context": m.context} for m in messages]
