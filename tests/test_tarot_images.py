"""Tests for tarot card image assets."""

from __future__ import annotations

import pytest

from src.tarot.images import CARD_BACK_SLUG, CARD_SLUGS, card_back_path, card_image_path, random_cards


@pytest.mark.parametrize("slug", CARD_SLUGS)
def test_card_image_exists(slug: str) -> None:
    """Every Major Arcana card slug should map to an existing PNG file."""
    path = card_image_path(slug)
    assert path.exists(), f"Missing card image: {path}"
    assert path.suffix == ".png"
    size_mb = path.stat().st_size / (1024 * 1024)
    assert size_mb < 5, f"Card image too large ({size_mb:.1f} MB): {path}"


def test_card_back_exists() -> None:
    """Card-back image should exist."""
    path = card_back_path()
    assert path.exists(), f"Missing card back image: {path}"
    assert path.suffix == ".png"
    size_mb = path.stat().st_size / (1024 * 1024)
    assert size_mb < 5, f"Card back too large ({size_mb:.1f} MB): {path}"


def test_total_card_count() -> None:
    """Should have exactly 22 Major Arcana cards."""
    assert len(CARD_SLUGS) == 22, f"Expected 22 Major Arcana, got {len(CARD_SLUGS)}"


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
