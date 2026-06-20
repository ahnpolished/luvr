import sys
from types import SimpleNamespace
from typing import Any

import pytest

from src.eval_workflow import (
    DEFAULT_CONVERSATION_EVAL_NAME,
    build_conversation_eval_cases,
    run_weave_conversation_eval,
)


def test_builds_default_conversation_eval_cases() -> None:
    cases = build_conversation_eval_cases()

    assert [case.name for case in cases] == [
        "friend_like_support",
        "safety_escalation",
        "boundary_respect",
    ]
    assert all(case.user_input for case in cases)
    assert all(case.expected_behavior for case in cases)


def test_unknown_conversation_eval_name_fails_fast() -> None:
    with pytest.raises(ValueError, match="Unknown conversation eval workflow"):
        build_conversation_eval_cases("unknown-eval")


def test_weave_runner_initializes_project_and_evaluates(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: dict[str, Any] = {}

    class FakeEvaluation:
        def __init__(self, *, name: str, dataset: list[dict[str, Any]]) -> None:
            calls["name"] = name
            calls["dataset"] = dataset

        def evaluate(self, predict: Any) -> dict[str, Any]:
            calls["predict"] = predict
            return {"ok": True}

    fake_weave = SimpleNamespace(
        init=lambda project: calls.setdefault("project", project),
        Evaluation=FakeEvaluation,
    )
    monkeypatch.setitem(sys.modules, "weave", fake_weave)

    result = run_weave_conversation_eval(
        predict=lambda row: {"response": row["user_input"]},
        project="humphreyahn/luvr",
    )

    assert result == {"ok": True}
    assert calls["project"] == "humphreyahn/luvr"
    assert calls["name"] == DEFAULT_CONVERSATION_EVAL_NAME
    assert len(calls["dataset"]) == 3
    assert calls["dataset"][0]["tags"] == ["tone", "friend-like"]
    assert callable(calls["predict"])
