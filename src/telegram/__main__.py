"""Support ``python -m src.telegram`` as a convenience alias."""

from __future__ import annotations

from src.telegram_server import main

if __name__ == "__main__":
    main()
