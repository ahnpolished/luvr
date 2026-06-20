from datetime import UTC, datetime, timedelta

import pytest

from src.eval_trace_policy import EvalTracePolicy, TraceConsent


def test_trace_capture_requires_alpha_consent() -> None:
    policy = EvalTracePolicy()

    assert policy.can_capture(TraceConsent(alpha_user=True, eval_tracing=True))
    assert not policy.can_capture(TraceConsent(alpha_user=True, eval_tracing=False))
    assert not policy.can_capture(TraceConsent(alpha_user=False, eval_tracing=True))


@pytest.mark.parametrize("retention_days", [6, 31])
def test_trace_retention_must_stay_in_alpha_window(retention_days: int) -> None:
    with pytest.raises(ValueError, match="between 7 and 30 days"):
        EvalTracePolicy(retention_days=retention_days)


def test_trace_expiration_uses_configured_retention() -> None:
    captured_at = datetime(2026, 6, 20, 12, 0, tzinfo=UTC)
    policy = EvalTracePolicy(retention_days=14)

    assert policy.expires_at(captured_at) == captured_at + timedelta(days=14)


def test_trace_expiration_requires_timezone_aware_time() -> None:
    policy = EvalTracePolicy()

    with pytest.raises(ValueError, match="timezone-aware"):
        policy.expires_at(datetime(2026, 6, 20, 12, 0))
