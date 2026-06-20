"""Alpha eval trace consent and retention policy."""

from dataclasses import dataclass
from datetime import datetime, timedelta

MIN_TRACE_RETENTION_DAYS = 7
MAX_TRACE_RETENTION_DAYS = 30
DEFAULT_TRACE_RETENTION_DAYS = 14


@dataclass(frozen=True)
class TraceConsent:
    """Consent inputs required before capturing eval traces for an alpha user."""

    alpha_user: bool
    eval_tracing: bool


@dataclass(frozen=True)
class EvalTracePolicy:
    """Policy gate for alpha eval trace capture and retention."""

    retention_days: int = DEFAULT_TRACE_RETENTION_DAYS

    def __post_init__(self) -> None:
        if not MIN_TRACE_RETENTION_DAYS <= self.retention_days <= MAX_TRACE_RETENTION_DAYS:
            raise ValueError(
                "Eval trace retention must be between "
                f"{MIN_TRACE_RETENTION_DAYS} and {MAX_TRACE_RETENTION_DAYS} days"
            )

    def can_capture(self, consent: TraceConsent) -> bool:
        return consent.alpha_user and consent.eval_tracing

    def expires_at(self, captured_at: datetime) -> datetime:
        if captured_at.tzinfo is None or captured_at.utcoffset() is None:
            raise ValueError("Eval trace capture time must be timezone-aware")

        return captured_at + timedelta(days=self.retention_days)
