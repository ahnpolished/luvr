"""Pytest conftest for DeepEval evaluation suite.

Registers eval markers and configures the test environment.
"""

from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers for eval tests."""
    config.addinivalue_line("markers", "eval: mark test as an AI evaluation case")
    config.addinivalue_line("markers", "slow: mark test as slow (full eval suite)")


def pytest_collection_modifyitems(
    session: pytest.Session, config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Skip eval tests unless explicitly requested with -m eval."""
    # Auto-skip eval tests by default — they're opt-in
    # but always run in CI via the dedicated eval step
    pass
