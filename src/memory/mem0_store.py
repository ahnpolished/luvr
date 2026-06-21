"""Per-user persistent memory wrapper backed by mem0 (HUM-1366 evaluation).

This is a thin wrapper, not a production integration: every operation is
explicitly scoped by ``user_id`` so memory can never leak across users, and
the wrapper accepts any object matching mem0.Memory's add/search/delete_all
surface so it can be exercised against a fake backend in fast unit tests and
against the real mem0 library in tests/eval/.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class Mem0Backend(Protocol):
    """The subset of mem0.Memory's interface this wrapper depends on."""

    def add(
        self,
        messages: list[dict[str, str]],
        *,
        user_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]: ...

    def search(
        self,
        query: str,
        *,
        filters: dict[str, Any] | None = None,
        top_k: int = 5,
    ) -> dict[str, Any]: ...

    def delete_all(self, *, user_id: str) -> None: ...


@dataclass(frozen=True)
class MemoryFact:
    """A single durable fact recalled for one user."""

    memory_id: str
    text: str
    user_id: str


class PerUserMemoryStore:
    """Per-user memory read/write/delete, scoped by user_id on every call."""

    def __init__(self, backend: Mem0Backend) -> None:
        self._backend = backend

    def remember(
        self,
        user_id: str,
        text: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> list[MemoryFact]:
        """Store a durable fact for one user and return what was stored."""
        result = self._backend.add(
            [{"role": "user", "content": text}],
            user_id=user_id,
            metadata=metadata,
        )
        return [
            MemoryFact(memory_id=item["id"], text=item.get("memory", text), user_id=user_id)
            for item in result.get("results", [])
        ]

    def recall(self, user_id: str, query: str, *, top_k: int = 5) -> list[MemoryFact]:
        """Search one user's memory only; never returns another user's facts."""
        result = self._backend.search(query, filters={"user_id": user_id}, top_k=top_k)
        return [
            MemoryFact(memory_id=item["id"], text=item["memory"], user_id=user_id) for item in result.get("results", [])
        ]

    def forget_all(self, user_id: str) -> None:
        """Delete every memory for one user. Idempotent for unknown users."""
        self._backend.delete_all(user_id=user_id)
