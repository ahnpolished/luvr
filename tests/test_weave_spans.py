import sys
from contextlib import contextmanager
from types import SimpleNamespace
from typing import Any

import pytest

from src.weave_spans import ConversationSpanAttributes, conversation_span_attributes


def test_conversation_span_attributes_drop_empty_optional_labels() -> None:
    attributes = ConversationSpanAttributes(
        message_type="telegram_text",
        model="gpt-4o-mini",
        latency_ms=123,
        alpha_user_id="alpha_123",
        display_name="Tae",
        nickname=None,
    )

    assert attributes.as_weave_attributes() == {
        "message_type": "telegram_text",
        "model": "gpt-4o-mini",
        "latency_ms": 123,
        "alpha_user_id": "alpha_123",
        "display_name": "Tae",
    }


@pytest.mark.parametrize(
    ("attributes", "match"),
    [
        (ConversationSpanAttributes(message_type="", model="gpt-4o-mini"), "message_type"),
        (ConversationSpanAttributes(message_type="telegram_text", model=""), "model"),
        (
            ConversationSpanAttributes(
                message_type="telegram_text",
                model="gpt-4o-mini",
                latency_ms=-1,
            ),
            "latency_ms",
        ),
    ],
)
def test_conversation_span_attributes_validate_required_fields(
    attributes: ConversationSpanAttributes,
    match: str,
) -> None:
    with pytest.raises(ValueError, match=match):
        attributes.as_weave_attributes()


def test_conversation_span_attributes_wraps_weave_attributes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: dict[str, Any] = {}

    @contextmanager
    def fake_attributes(labels: dict[str, Any]):
        calls["labels"] = labels
        yield
        calls["exited"] = True

    monkeypatch.setitem(sys.modules, "weave", SimpleNamespace(attributes=fake_attributes))

    with conversation_span_attributes(ConversationSpanAttributes(message_type="telegram_text", model="gpt-4o-mini")):
        calls["inside"] = True

    assert calls == {
        "labels": {"message_type": "telegram_text", "model": "gpt-4o-mini"},
        "inside": True,
        "exited": True,
    }


def test_conversation_span_attributes_noops_without_weave(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.weave_spans as weave_spans

    def raise_missing_module(_: str):
        raise ModuleNotFoundError

    monkeypatch.setattr(weave_spans, "import_module", raise_missing_module)
    with conversation_span_attributes({"message_type": "telegram_text"}):
        assert True
