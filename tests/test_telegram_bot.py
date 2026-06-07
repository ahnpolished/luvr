"""Tests for LuvrBot class."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.telegram.bot import LuvrBot


def test_bot_initialization():
    """Test bot initializes with correct config."""
    bot = LuvrBot(
        token="test-token",
        mode="polling",
    )
    assert bot.token == "test-token"
    assert bot.mode == "polling"
    assert bot.webhook_url is None
    assert bot.allowed_user_ids == set()
    assert bot._llm_client is None
    assert bot._bridge_client is None
    assert bot._app is None


def test_bot_initialization_with_webhook():
    """Test bot initializes with webhook config."""
    bot = LuvrBot(
        token="test-token",
        mode="webhook",
        webhook_url="https://example.com/webhook",
        allowed_user_ids=[123, 456],
    )
    assert bot.mode == "webhook"
    assert bot.webhook_url == "https://example.com/webhook"
    assert bot.allowed_user_ids == {123, 456}


def test_bot_llm_client_lazy_init():
    """Test LLM client is lazily initialized."""
    with patch("src.telegram.bot.create_llm_client") as mock_create:
        mock_create.return_value = MagicMock()
        bot = LuvrBot(token="test-token")
        assert bot._llm_client is None
        _ = bot.llm_client
        assert bot._llm_client is not None
        mock_create.assert_called_once()


def test_bot_bridge_client_lazy_init():
    """Test bridge client is lazily initialized."""
    bot = LuvrBot(token="test-token")
    assert bot._bridge_client is None
    bc = bot.bridge_client
    assert bot._bridge_client is not None
    assert bc is bot.bridge_client  # singleton


def test_bot_app_before_start_raises():
    """Test accessing app before start raises RuntimeError."""
    bot = LuvrBot(token="test-token")
    with pytest.raises(RuntimeError, match="not started"):
        _ = bot.app


@pytest.mark.asyncio
async def test_bot_start_polling():
    """Test bot starts in polling mode."""
    with (
        patch("src.telegram.bot.create_llm_client") as mock_llm,
        patch("src.telegram.bot.ApplicationBuilder") as mock_builder_cls,
    ):
        mock_llm.return_value = MagicMock()

        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder_cls.return_value = mock_builder

        mock_app = MagicMock()
        mock_app.bot_data = {}
        mock_app.updater = MagicMock()
        mock_app.updater.start_polling = AsyncMock()
        mock_app.initialize = AsyncMock()
        mock_app.start = AsyncMock()
        mock_builder.build.return_value = mock_app

        bot = LuvrBot(token="test-token", mode="polling")
        await bot.start()

        assert bot._app is not None
        assert "bridge_client" in mock_app.bot_data
        assert "llm_client" in mock_app.bot_data
        mock_app.updater.start_polling.assert_called_once()


@pytest.mark.asyncio
async def test_bot_start_webhook():
    """Test bot starts in webhook mode."""
    with (
        patch("src.telegram.bot.create_llm_client") as mock_llm,
        patch("src.telegram.bot.ApplicationBuilder") as mock_builder_cls,
    ):
        mock_llm.return_value = MagicMock()

        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder_cls.return_value = mock_builder

        mock_app = MagicMock()
        mock_app.bot_data = {}
        mock_app.bot = MagicMock()
        mock_app.bot.set_webhook = AsyncMock()
        mock_builder.build.return_value = mock_app

        bot = LuvrBot(
            token="test-token",
            mode="webhook",
            webhook_url="https://example.com/webhook",
        )
        await bot.start()

        mock_app.bot.set_webhook.assert_called_once_with(url="https://example.com/webhook")


@pytest.mark.asyncio
async def test_bot_stop():
    """Test bot stops gracefully."""
    with (
        patch("src.telegram.bot.create_llm_client") as mock_llm,
    ):
        mock_llm.return_value = MagicMock()
        bot = LuvrBot(token="test-token")

        mock_app = MagicMock()
        mock_app.updater = MagicMock()
        mock_app.updater.stop = AsyncMock()
        mock_app.stop = AsyncMock()
        mock_app.shutdown = AsyncMock()
        bot._app = mock_app

        bot._bridge_client = MagicMock()
        bot._bridge_client.aclose = AsyncMock()

        await bot.stop()

        bot._bridge_client.aclose.assert_called_once()
        assert bot._app is None


@pytest.mark.asyncio
async def test_bot_stop_error_handling():
    """Test bot stop handles errors gracefully."""
    with patch("src.telegram.bot.create_llm_client") as mock_llm:
        mock_llm.return_value = MagicMock()
        bot = LuvrBot(token="test-token")

        mock_app = MagicMock()
        mock_app.updater = MagicMock()
        mock_app.updater.stop = AsyncMock(side_effect=Exception("Shutdown error"))
        bot._app = mock_app

        # Should not raise
        await bot.stop()
        assert bot._app is None


@pytest.mark.asyncio
async def test_bot_stop_without_updater():
    """Test stop when updater doesn't exist."""
    with patch("src.telegram.bot.create_llm_client") as mock_llm:
        mock_llm.return_value = MagicMock()
        bot = LuvrBot(token="test-token")

        mock_app = MagicMock()
        mock_app.updater = None
        mock_app.stop = AsyncMock()
        mock_app.shutdown = AsyncMock()
        bot._app = mock_app

        await bot.stop()

        mock_app.stop.assert_called_once()
        assert bot._app is None


def test_build_handler():
    """Test _build_handler wraps handler with dependency injection."""
    from src.telegram.bot import _build_handler

    handler_fn = AsyncMock()
    wrapper = _build_handler(handler_fn)

    # Should be callable
    assert callable(wrapper)


@pytest.mark.asyncio
async def test_build_handler_calls_inner():
    """Test _build_handler passes bridge_client and llm_client from context."""
    from src.telegram.bot import _build_handler

    handler_fn = AsyncMock()
    wrapper = _build_handler(handler_fn)

    mock_bc = MagicMock()
    mock_llm = MagicMock()
    mock_context = MagicMock()
    mock_context.bot_data = {"bridge_client": mock_bc, "llm_client": mock_llm}
    mock_update = MagicMock()

    await wrapper(mock_update, mock_context)

    handler_fn.assert_called_once_with(mock_update, mock_context, bridge_client=mock_bc, llm_client=mock_llm)


@pytest.mark.asyncio
async def test_bot_stop_no_app():
    """Test calling stop when bot was never started."""
    with patch("src.telegram.bot.create_llm_client") as mock_llm:
        mock_llm.return_value = MagicMock()
        bot = LuvrBot(token="test-token")

        # Should not raise
        await bot.stop()
