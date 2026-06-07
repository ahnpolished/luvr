"""Telegram bot entrypoint for the Luvr dating advice chatbot.

Usage::

    python -m src.telegram_server
    luvr-telegram
    luvr-telegram --mode webhook --webhook-url https://example.com/webhook
"""

from __future__ import annotations

import argparse
import asyncio
import sys

import structlog

from src.config import settings
from src.logging_config import setup_logging
from src.telegram.bot import LuvrBot

logger = structlog.get_logger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the Telegram bot."""
    parser = argparse.ArgumentParser(
        prog="luvr-telegram",
        description="💝 Luvr Telegram bot — dating advice via Telegram",
    )
    parser.add_argument(
        "--mode",
        choices=["polling", "webhook"],
        default=None,
        help="Override TELEGRAM_MODE from .env (default: polling)",
    )
    parser.add_argument(
        "--webhook-url",
        default=None,
        help="Override TELEGRAM_WEBHOOK_URL from .env",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug-level logging",
    )
    return parser.parse_args(argv)


async def async_main() -> None:
    """Async entrypoint — configures logging, creates bot, and runs it."""
    args = parse_args()

    setup_logging()

    if args.verbose:
        import logging

        logging.getLogger().setLevel("DEBUG")

    # Resolve mode: CLI arg > env var > default
    mode = args.mode or settings.telegram_mode or "polling"
    webhook_url = args.webhook_url or settings.telegram_webhook_url

    if not settings.telegram_bot_token:
        logger.error("missing_telegram_bot_token")
        print("❌ TELEGRAM_BOT_TOKEN is required. Set it in .env or environment.")
        sys.exit(1)

    # Parse allowed user IDs from config
    allowed_ids = settings.telegram_allowed_user_id_list

    bot = LuvrBot(
        token=settings.telegram_bot_token,
        mode=mode,
        webhook_url=webhook_url,
        allowed_user_ids=allowed_ids if allowed_ids else None,
    )

    try:
        await bot.run_until_sigterm()
    except KeyboardInterrupt:
        logger.info("keyboard_interrupt")
    except Exception:
        logger.exception("bot_fatal_error")
        sys.exit(1)


def main() -> None:
    """Synchronous entrypoint — runs the async event loop."""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
