"""Evaluation trace capture schema."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.eval_trace_policy import EvalTracePolicy


@dataclass(frozen=True)
class EvalTraceCapture:
    trace_id: str
    eval_name: str
    message_type: str
    model: str
    latency_ms: int
    captured_at: datetime
    metadata: dict[str, Any] | None = None

    def to_record(self, policy: EvalTracePolicy) -> dict[str, Any]:
        if not self.trace_id:
            raise ValueError("trace_id is required")
        if not self.eval_name:
            raise ValueError("eval_name is required")
        if not self.message_type:
            raise ValueError("message_type is required")
        if not self.model:
            raise ValueError("model is required")
        if self.latency_ms < 0:
            raise ValueError("latency_ms must be non-negative")

        return {
            "trace_id": self.trace_id,
            "eval_name": self.eval_name,
            "message_type": self.message_type,
            "model": self.model,
            "latency_ms": self.latency_ms,
            "captured_at": self.captured_at.isoformat(),
            "expires_at": policy.expires_at(self.captured_at).isoformat(),
            "metadata": self.metadata or {},
        }
