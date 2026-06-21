"""Tests for Telegram 3-card tarot reading flow."""

from __future__ import annotations

import pytest

from src.llm.tarot import MAJOR_ARCANA, TAROT_DECK, build_tarot_prompt

ENGLISH_NAMES = [c["name_en"] for c in MAJOR_ARCANA]


def test_tarot_deck_has_78_cards():
    assert len(TAROT_DECK) == 78
    assert len(set(c["id"] for c in TAROT_DECK)) == 78  # unique ids


def test_major_arcana_has_22_cards():
    assert len(MAJOR_ARCANA) == 22
    assert len(ENGLISH_NAMES) == len(set(ENGLISH_NAMES))


def test_build_tarot_prompt_en():
    prompt = build_tarot_prompt(
        selected_cards=["The Star", "The Lovers", "The Hermit"],
        user_language="en",
    )
    assert "3-card spread" in prompt
    assert "The Star" in prompt
    assert "The Lovers" in prompt
    assert "The Hermit" in prompt
    assert "dating and relationships" in prompt


def test_build_tarot_prompt_ko():
    prompt = build_tarot_prompt(
        selected_cards=["별 (The Star)", "연인 (The Lovers)", "은둔자 (The Hermit)"],
        user_language="ko",
    )
    assert "별 (The Star)" in prompt
    assert "한국어" in prompt


@pytest.mark.parametrize("card", ENGLISH_NAMES[:5])
def test_individual_card_has_both_names(card):
    entry = next(c for c in MAJOR_ARCANA if c["name_en"] == card)
    assert entry["name_ko"]
