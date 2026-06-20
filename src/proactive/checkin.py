"""Deterministic manual check-in copy for v0.1.0."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ManualCheckinInput:
    display_name: str | None = None
    context: str | None = None


def build_manual_checkin(input_data: ManualCheckinInput) -> str:
    name = input_data.display_name.strip() if input_data.display_name else ""
    context = input_data.context.strip() if input_data.context else ""

    greeting = f"Hey {name}" if name else "Hey"
    context_line = f" Still thinking about {context}." if context else ""

    return (
        f"{greeting}, quick check-in.{context_line} "
        "Want to talk through what happened, or should I help you draft the next text?"
    )
