from datetime import UTC, datetime

import pytest

from src.eval_trace_policy import EvalTracePolicy
from src.eval_trace_schema import EvalTraceCapture


def _trace(**overrides):
    values = {
        "trace_id": "trace_123",
        "eval_name": "luvr-eval-v1",
        "message_type": "telegram_text",
        "model": "gpt-4o-mini",
        "latency_ms": 250,
        "captured_at": datetime(2026, 6, 20, 12, 0, tzinfo=UTC),
        "metadata": {"case": "friend_like_support"},
    }
    values.update(overrides)
    return EvalTraceCapture(**values)


def test_eval_trace_capture_record_includes_retention_expiration() -> None:
    record = _trace().to_record(EvalTracePolicy(retention_days=7))

    assert record == {
        "trace_id": "trace_123",
        "eval_name": "luvr-eval-v1",
        "message_type": "telegram_text",
        "model": "gpt-4o-mini",
        "latency_ms": 250,
        "captured_at": "2026-06-20T12:00:00+00:00",
        "expires_at": "2026-06-27T12:00:00+00:00",
        "metadata": {"case": "friend_like_support"},
    }


@pytest.mark.parametrize("field", ["trace_id", "eval_name", "message_type", "model"])
def test_eval_trace_capture_requires_named_fields(field: str) -> None:
    trace = _trace(**{field: ""})

    with pytest.raises(ValueError, match=field):
        trace.to_record(EvalTracePolicy())


def test_eval_trace_capture_requires_non_negative_latency() -> None:
    with pytest.raises(ValueError, match="latency_ms"):
        _trace(latency_ms=-1).to_record(EvalTracePolicy())
