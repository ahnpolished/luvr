#!/usr/bin/env python3
"""
Luvr Telegram Bot — Standalone Working Example
===============================================

This is a self-contained example that demonstrates how to run the Luvr
dating advice chatbot as a Telegram bot.  It uses the same LLM integration
and prompts as the iMessage version but connects via the Telegram Bot API.

Requirements
------------
1. A Telegram bot token from @BotFather → set TELEGRAM_BOT_TOKEN in .env
2. An OpenAI API key → set OPENAI_API_KEY in .env
3. OR an Anthropic API key → set ANTHROPIC_API_KEY + LLM_PROVIDER=anthropic

Quick Start
-----------
    export TELEGRAM_BOT_TOKEN="123456:ABC-DEF..."
    export OPENAI_API_KEY="sk-..."
    python examples/telegram_bot.py

Or use the project's .env:
    cp .env.example .env
    # edit .env with your keys
    python examples/telegram_bot.py
"""

from __future__ import annotations

import asyncio
import os
import signal
import sys
from pathlib import Path

# Ensure the project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import settings  # noqa: E402 — need path first
from src.logging_config import setup_logging  # noqa: E402
from src.telegram.bot import LuvrBot  # noqa: E402


async def main():
    setup_logging()

    token = os.getenv("TELEGRAM_BOT_TOKEN") or settings.telegram_bot_token
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN is required.")
        print("   Set it in .env or export TELEGRAM_BOT_TOKEN=...")
        sys.exit(1)

    print("💝 Luvr Telegram Bot")
    print(f"   LLM Provider: {settings.llm_provider}")
    print(f"   LLM Model:    {settings.llm_model}")
    print(f"   Mode:         {settings.telegram_mode}")
    print()
    print("   Send /start to your bot on Telegram to begin!")
    print("   Press Ctrl+C to stop.")
    print()

    bot = LuvrBot(
        token=token,
        mode=settings.telegram_mode,
        webhook_url=settings.telegram_webhook_url,
        allowed_user_ids=list(settings.telegram_allowed_user_ids)
        if settings.telegram_allowed_user_ids
        else None,
    )

    await bot.start()
    print("✅ Bot is running. Waiting for messages...")

    # Block until signal
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop_event.set)
        except NotImplementedError:
            pass

    await stop_event.wait()
    await bot.stop()
    print("👋 Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
