"""Optional Weave span helpers for alpha conversation instrumentation."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
from importlib import import_module
from typing import Any


@dataclass(frozen=True)
class ConversationSpanAttributes:
    message_type: str
    model: str
    latency_ms: int | None = None
    alpha_user_id: str | None = None
    display_name: str | None = None
    nickname: str | None = None

    def as_weave_attributes(self) -> dict[str, Any]:
        if not self.message_type:
            raise ValueError("message_type is required")
        if not self.model:
            raise ValueError("model is required")
        if self.latency_ms is not None and self.latency_ms < 0:
            raise ValueError("latency_ms must be non-negative")

        attributes: dict[str, Any] = {
            "message_type": self.message_type,
            "model": self.model,
            "latency_ms": self.latency_ms,
            "alpha_user_id": self.alpha_user_id,
            "display_name": self.display_name,
            "nickname": self.nickname,
        }
        return {key: value for key, value in attributes.items() if value is not None}


@contextmanager
def conversation_span_attributes(
    attributes: ConversationSpanAttributes | Mapping[str, Any],
) -> Iterator[None]:
    labels = (
        attributes.as_weave_attributes()
        if isinstance(attributes, ConversationSpanAttributes)
        else {key: value for key, value in attributes.items() if value is not None}
    )

    try:
        weave = import_module("weave")
    except ModuleNotFoundError:
        yield
        return

    weave_attributes = getattr(weave, "attributes", None)
    span_context = weave_attributes(labels) if labels and callable(weave_attributes) else nullcontext()
    with span_context:
        yield
