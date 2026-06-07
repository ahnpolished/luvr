"""CLI entrypoint for the Telegram bot (console_scripts hook)."""

from __future__ import annotations

from src.telegram_server import main

if __name__ == "__main__":
    main()
