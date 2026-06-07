"""Tests for Telegram server entrypoint and CLI."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.telegram_server import parse_args


class TestParseArgs:
    """Tests for CLI argument parsing."""

    def test_default_args(self):
        """Test default arguments."""
        args = parse_args([])
        assert args.mode is None
        assert args.webhook_url is None
        assert args.verbose is False

    def test_mode_polling(self):
        """Test --mode polling."""
        args = parse_args(["--mode", "polling"])
        assert args.mode == "polling"

    def test_mode_webhook(self):
        """Test --mode webhook."""
        args = parse_args(["--mode", "webhook"])
        assert args.mode == "webhook"

    def test_mode_invalid(self):
        """Test invalid mode is rejected."""
        with pytest.raises(SystemExit):
            parse_args(["--mode", "invalid"])

    def test_webhook_url(self):
        """Test --webhook-url argument."""
        args = parse_args(["--webhook-url", "https://example.com/webhook"])
        assert args.webhook_url == "https://example.com/webhook"

    def test_verbose(self):
        """Test --verbose flag."""
        args = parse_args(["--verbose"])
        assert args.verbose is True

    def test_all_args(self):
        """Test all arguments together."""
        args = parse_args([
            "--mode", "webhook",
            "--webhook-url", "https://example.com/webhook",
            "--verbose",
        ])
        assert args.mode == "webhook"
        assert args.webhook_url == "https://example.com/webhook"
        assert args.verbose is True


class TestAsyncMain:
    """Tests for the async_main function."""

    @pytest.mark.asyncio
    async def test_async_main_missing_token(self):
        """Test async_main exits when token is missing."""
        with (
            patch("src.telegram_server.parse_args") as mock_parse,
            patch("src.telegram_server.setup_logging"),
            patch("src.telegram_server.settings") as mock_settings,
            patch("sys.exit") as mock_exit,
        ):
            mock_parse.return_value = MagicMock(mode=None, webhook_url=None, verbose=False)
            mock_settings.telegram_bot_token = ""
            mock_settings.telegram_mode = "polling"
            mock_settings.telegram_webhook_url = None
            mock_settings.telegram_allowed_user_id_list = []

            from src.telegram_server import async_main

            await async_main()

            # May be called multiple times (exit + exception handler)
            mock_exit.assert_any_call(1)

    @pytest.mark.asyncio
    async def test_async_main_starts_bot(self):
        """Test async_main starts the bot successfully."""
        with (
            patch("src.telegram_server.parse_args") as mock_parse,
            patch("src.telegram_server.setup_logging"),
            patch("src.telegram_server.settings") as mock_settings,
            patch("src.telegram_server.LuvrBot") as MockBot,
        ):
            mock_parse.return_value = MagicMock(
                mode=None, webhook_url=None, verbose=False
            )
            mock_settings.telegram_bot_token = "test-token"
            mock_settings.telegram_mode = "polling"
            mock_settings.telegram_webhook_url = None
            mock_settings.telegram_allowed_user_id_list = []

            mock_bot = MagicMock()
            mock_bot.run_until_sigterm = AsyncMock()
            MockBot.return_value = mock_bot

            from src.telegram_server import async_main

            await async_main()

            MockBot.assert_called_once_with(
                token="test-token",
                mode="polling",
                webhook_url=None,
                allowed_user_ids=None,
            )
            mock_bot.run_until_sigterm.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_main_with_webhook(self):
        """Test async_main with webhook mode from CLI args."""
        with (
            patch("src.telegram_server.parse_args") as mock_parse,
            patch("src.telegram_server.setup_logging"),
            patch("src.telegram_server.settings") as mock_settings,
            patch("src.telegram_server.LuvrBot") as MockBot,
        ):
            mock_parse.return_value = MagicMock(
                mode="webhook",
                webhook_url="https://example.com/webhook",
                verbose=False,
            )
            mock_settings.telegram_bot_token = "test-token"
            mock_settings.telegram_mode = "polling"
            mock_settings.telegram_webhook_url = None
            mock_settings.telegram_allowed_user_id_list = []

            mock_bot = MagicMock()
            mock_bot.run_until_sigterm = AsyncMock()
            MockBot.return_value = mock_bot

            from src.telegram_server import async_main

            await async_main()

            MockBot.assert_called_once_with(
                token="test-token",
                mode="webhook",
                webhook_url="https://example.com/webhook",
                allowed_user_ids=None,
            )

    @pytest.mark.asyncio
    async def test_async_main_with_allowed_ids(self):
        """Test async_main with allowed user IDs."""
        with (
            patch("src.telegram_server.parse_args") as mock_parse,
            patch("src.telegram_server.setup_logging"),
            patch("src.telegram_server.settings") as mock_settings,
            patch("src.telegram_server.LuvrBot") as MockBot,
        ):
            mock_parse.return_value = MagicMock(
                mode=None, webhook_url=None, verbose=False
            )
            mock_settings.telegram_bot_token = "test-token"
            mock_settings.telegram_mode = "polling"
            mock_settings.telegram_webhook_url = None
            mock_settings.telegram_allowed_user_id_list = [123, 456, 789]

            mock_bot = MagicMock()
            mock_bot.run_until_sigterm = AsyncMock()
            MockBot.return_value = mock_bot

            from src.telegram_server import async_main

            await async_main()

            MockBot.assert_called_once_with(
                token="test-token",
                mode="polling",
                webhook_url=None,
                allowed_user_ids=[123, 456, 789],
            )

    @pytest.mark.asyncio
    async def test_async_main_keyboard_interrupt(self):
        """Test async_main handles KeyboardInterrupt."""
        with (
            patch("src.telegram_server.parse_args") as mock_parse,
            patch("src.telegram_server.setup_logging"),
            patch("src.telegram_server.settings") as mock_settings,
            patch("src.telegram_server.LuvrBot") as MockBot,
        ):
            mock_parse.return_value = MagicMock(
                mode=None, webhook_url=None, verbose=False
            )
            mock_settings.telegram_bot_token = "test-token"
            mock_settings.telegram_mode = "polling"
            mock_settings.telegram_webhook_url = None
            mock_settings.telegram_allowed_user_id_list = []

            mock_bot = MagicMock()
            mock_bot.run_until_sigterm = AsyncMock(side_effect=KeyboardInterrupt())
            MockBot.return_value = mock_bot

            from src.telegram_server import async_main

            # Should not raise
            await async_main()

    @pytest.mark.asyncio
    async def test_async_main_fatal_error(self):
        """Test async_main handles fatal bot errors."""
        with (
            patch("src.telegram_server.parse_args") as mock_parse,
            patch("src.telegram_server.setup_logging"),
            patch("src.telegram_server.settings") as mock_settings,
            patch("src.telegram_server.LuvrBot") as MockBot,
            patch("sys.exit") as mock_exit,
        ):
            mock_parse.return_value = MagicMock(
                mode=None, webhook_url=None, verbose=False
            )
            mock_settings.telegram_bot_token = "test-token"
            mock_settings.telegram_mode = "polling"
            mock_settings.telegram_webhook_url = None
            mock_settings.telegram_allowed_user_id_list = []

            mock_bot = MagicMock()
            mock_bot.run_until_sigterm = AsyncMock(side_effect=RuntimeError("Fatal"))
            MockBot.return_value = mock_bot

            from src.telegram_server import async_main

            await async_main()

            mock_exit.assert_called_with(1)


def test_main_function():
    """Test the synchronous main() entrypoint."""
    with (
        patch("src.telegram_server.async_main", new=AsyncMock()) as mock_am,
        patch("asyncio.run") as mock_run,
    ):
        from src.telegram_server import main

        main()

        mock_run.assert_called_once()
