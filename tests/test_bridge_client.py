"""Tests for BlueBubbles bridge client."""

from __future__ import annotations

import pytest
from src.bridge.client import BlueBubblesClient


def test_client_initialization():
    """Test BlueBubbles client is created with correct config."""
    client = BlueBubblesClient(
        server_url="http://localhost:1234",
        password="test_password",
    )
    assert client.server_url == "http://localhost:1234"
    assert client.password == "test_password"
    assert client._client is None  # Lazy init


def test_client_lazy_init():
    """Test that HTTP client is lazily initialized."""
    client = BlueBubblesClient(
        server_url="http://localhost:1234",
        password="test_password",
    )
    assert client._client is None
    c = client.client  # Access triggers init
    assert client._client is not None


@pytest.mark.asyncio
async def test_aclose():
    """Test that aclose cleans up the client."""
    client = BlueBubblesClient(
        server_url="http://localhost:1234",
        password="test_password",
    )
    # Force init
    _ = client.client
    assert client._client is not None

    await client.aclose()
    assert client._client is None
