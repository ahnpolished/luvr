"""Spread position definitions for the 3-card relationship reading."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    key: str
    title: str
    description: str


RELATIONSHIP_SPREAD: list[Position] = [
    Position(
        key="situation",
        title="Where you are",
        description="What is actually happening between you two right now.",
    ),
    Position(
        key="tension",
        title="Beneath the surface",
        description="The dynamic, fear, or mismatch making this feel unclear.",
    ),
    Position(
        key="next_move",
        title="Where it's heading",
        description="Where this is heading if nothing changes.",
    ),
]
