"""Deterministic v0.1.0 tarot UX flow."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TarotSlot:
    key: str
    title: str
    prompt: str


@dataclass(frozen=True)
class TarotFlow:
    key: str
    title: str
    intro: str
    slots: tuple[TarotSlot, ...]
    completion_cta: str


THREE_CARD_TAROT_FLOW = TarotFlow(
    key="three_card_relationship",
    title="3-card relationship read",
    intro="Pull three cards for the situation, the tension, and the next move.",
    slots=(
        TarotSlot(
            key="situation",
            title="Situation",
            prompt="What is actually happening between you two right now.",
        ),
        TarotSlot(
            key="tension",
            title="Tension",
            prompt="The dynamic, fear, or mismatch making this feel unclear.",
        ),
        TarotSlot(
            key="next_move",
            title="Next move",
            prompt="One grounded action to take without forcing the outcome.",
        ),
    ),
    completion_cta="Keep it practical: one insight, one next step, no fate talk.",
)
