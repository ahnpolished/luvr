"""Unit tests for the per-user mem0 memory wrapper.

Uses a fake mem0-shaped backend so these run fast and deterministic in the
default CI gate, with no network/API key required. Realistic evaluation
against the real mem0 library lives in tests/eval/test_mem0_realistic_eval.py.
"""

from __future__ import annotations

from typing import Any

import pytest

from src.memory.mem0_store import MemoryFact, PerUserMemoryStore


class FakeMem0Backend:
    """In-memory stand-in for mem0.Memory's add/search/delete_all surface."""

    def __init__(self) -> None:
        self._facts: dict[str, list[dict[str, Any]]] = {}
        self._next_id = 0

    def add(
        self,
        messages: list[dict[str, str]],
        *,
        user_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        results = []
        for message in messages:
            self._next_id += 1
            memory_id = f"mem-{self._next_id}"
            entry = {"id": memory_id, "memory": message["content"]}
            self._facts.setdefault(user_id, []).append(entry)
            results.append(entry)
        return {"results": results}

    def search(
        self,
        query: str,
        *,
        filters: dict[str, Any] | None = None,
        top_k: int = 5,
    ) -> dict[str, Any]:
        user_id = (filters or {}).get("user_id")
        candidates = self._facts.get(user_id, [])
        matches = [entry for entry in candidates if query.lower() in entry["memory"].lower()]
        return {"results": matches[:top_k]}

    def delete_all(self, *, user_id: str) -> None:
        self._facts.pop(user_id, None)

    def get_all(self, *, user_id: str) -> dict[str, Any]:
        return {"results": self._facts.get(user_id, [])}


@pytest.fixture
def store() -> PerUserMemoryStore:
    return PerUserMemoryStore(FakeMem0Backend())


def test_remember_returns_stored_fact(store: PerUserMemoryStore) -> None:
    facts = store.remember("user-a", "Looking for a long-term relationship")

    assert len(facts) == 1
    assert isinstance(facts[0], MemoryFact)
    assert facts[0].user_id == "user-a"
    assert "long-term relationship" in facts[0].text


def test_recall_finds_relevant_fact(store: PerUserMemoryStore) -> None:
    store.remember("user-a", "Prefers casual, low-pressure first dates")

    results = store.recall("user-a", query="casual")

    assert len(results) == 1
    assert "casual" in results[0].text.lower()


def test_recall_returns_empty_when_no_match(store: PerUserMemoryStore) -> None:
    store.remember("user-a", "Prefers casual, low-pressure first dates")

    results = store.recall("user-a", query="long-term goals")

    assert results == []


def test_memory_is_isolated_per_user(store: PerUserMemoryStore) -> None:
    store.remember("user-a", "Dating goal: long-term relationship")
    store.remember("user-b", "Dating goal: casual dating")

    a_results = store.recall("user-a", query="dating goal")
    b_results = store.recall("user-b", query="dating goal")

    assert len(a_results) == 1
    assert len(b_results) == 1
    assert "long-term" in a_results[0].text
    assert "casual" in b_results[0].text
    assert a_results[0].text != b_results[0].text


def test_forget_all_clears_only_target_user(store: PerUserMemoryStore) -> None:
    store.remember("user-a", "Dating goal: long-term relationship")
    store.remember("user-b", "Dating goal: casual dating")

    store.forget_all("user-a")

    assert store.recall("user-a", query="dating goal") == []
    assert len(store.recall("user-b", query="dating goal")) == 1


def test_forget_all_is_idempotent_for_unknown_user(store: PerUserMemoryStore) -> None:
    store.forget_all("user-with-no-memories")

    assert store.recall("user-with-no-memories", query="anything") == []


def test_remember_attaches_metadata(store: PerUserMemoryStore) -> None:
    facts = store.remember(
        "user-a",
        "Prefers Korean-language responses",
        metadata={"kind": "preference"},
    )

    assert len(facts) == 1
    assert facts[0].user_id == "user-a"


def test_realistic_multi_user_conversation_scenario(store: PerUserMemoryStore) -> None:
    """Three users with overlapping topics must never leak across user_id."""
    store.remember("alice", "Nervous about dating after a long break")
    store.remember("alice", "Wants advice on a second date with someone she met on a hike")
    store.remember("bob", "Recently divorced, taking things slow")
    store.remember("bob", "Wants advice on a second date with a coworker")
    store.remember("carol", "Looking for casual dating, not ready for commitment")

    alice_second_date = store.recall("alice", query="second date")
    bob_second_date = store.recall("bob", query="second date")
    carol_commitment = store.recall("carol", query="commitment")

    assert len(alice_second_date) == 1
    assert "hike" in alice_second_date[0].text
    assert len(bob_second_date) == 1
    assert "coworker" in bob_second_date[0].text
    assert len(carol_commitment) == 1
    assert "casual" in carol_commitment[0].text
