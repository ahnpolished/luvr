"""Tests for tarot card image assets."""

from __future__ import annotations

import pytest

from src.tarot.images import (
    CARD_BACK_SLUG,
    CARD_SLUGS,
    MAJOR_ARCANA_SLUGS,
    card_back_path,
    card_image_path,
    random_cards,
)


@pytest.mark.parametrize("slug", CARD_SLUGS[::8])  # evenly sample the 78-card deck (10 cards)
def test_card_image_exists_spot(slug: str) -> None:
    """Spot-check: every sampled card slug should map to an existing WebP file."""
    path = card_image_path(slug)
    assert path.exists(), f"Missing card image: {path}"
    assert path.suffix == ".webp"
    size_kb = path.stat().st_size / 1024
    assert size_kb < 500, f"Card image too large ({size_kb:.0f} KB): {path}"
    assert size_kb > 1, f"Card image too small ({size_kb:.0f} KB): {path}"


def test_card_back_exists() -> None:
    """Card-back image should exist (PNG)."""
    path = card_back_path()
    assert path.exists(), f"Missing card back image: {path}"
    assert path.suffix == ".png"
    size_kb = path.stat().st_size / 1024
    assert size_kb < 500, f"Card back too large ({size_kb:.0f} KB): {path}"


def test_total_card_count() -> None:
    """Should have exactly 78 cards: 22 Major + 56 Minor Arcana."""
    assert len(CARD_SLUGS) == 78, f"Expected 78 cards, got {len(CARD_SLUGS)}"
    assert len(MAJOR_ARCANA_SLUGS) == 22
    assert len(CARD_SLUGS) == len(set(CARD_SLUGS)), "Duplicate slugs"


def test_random_cards_no_duplicates() -> None:
    """random_cards() should return unique cards."""
    cards = random_cards(3)
    assert len(cards) == 3
    assert len(set(cards)) == 3
    for card in cards:
        assert card in CARD_SLUGS


def test_random_cards_respects_n() -> None:
    """random_cards(n) should return at most n cards."""
    assert len(random_cards(1)) == 1
    assert len(random_cards(5)) == 5
    assert len(random_cards(100)) == len(CARD_SLUGS)  # capped at deck size


def test_card_back_slug() -> None:
    """Card-back slug should be consistent."""
    assert CARD_BACK_SLUG == "card_back"
