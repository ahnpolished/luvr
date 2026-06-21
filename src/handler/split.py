"""Multi-bubble response splitting utility.

Splits LLM responses on the configured delimiter so each bubble can be
sent as a separate message with a natural typing delay.
"""

from __future__ import annotations

from src.config import settings


def split_response(response: str) -> list[str]:
    """Split a multi-bubble LLM response into individual messages.

    Bubbles are separated by the configured delimiter (default ``---BREAK---``).
    Empty bubbles and whitespace-only bubbles are stripped.

    If no delimiter is found, the entire response is returned as a single bubble
    so existing behaviour degrades gracefully.

    Args:
        response: Raw LLM response potentially containing delimiter markers.

    Returns:
        List of cleaned message strings, one per bubble.
    """
    delimiter = settings.multi_turn_delimiter

    if delimiter not in response:
        return [response.strip()]

    bubbles = [b.strip() for b in response.split(delimiter)]
    return [b for b in bubbles if b]
