"""Tests for language detection used in bilingual LLM responses."""

from __future__ import annotations

import pytest

from src.llm.language_detection import detect_language


def test_pure_english_returns_en():
    assert detect_language("Should I text him back tonight?") == "en"


def test_pure_korean_returns_ko():
    assert detect_language("오늘 데이트에서 무슨 말을 해야 할까요?") == "ko"


def test_mixed_korean_english_returns_mixed():
    assert detect_language("오빠가 ghosting 했어... what should I do?") == "mixed"


def test_korean_with_emoji_and_punctuation_returns_ko():
    assert detect_language("진짜요??? 😭 ㅠㅠ") == "ko"


def test_empty_or_whitespace_returns_default_en():
    assert detect_language("") == "en"
    assert detect_language("   ") == "en"


def test_numbers_and_symbols_only_returns_default_en():
    assert detect_language("12345 !!!") == "en"


def test_english_with_unicode_punctuation_returns_en():
    assert detect_language("Wait — don't text him!!!") == "en"


def test_short_korean_word_returns_ko():
    assert detect_language("고마워") == "ko"


@pytest.mark.parametrize(
    "text,expected",
    [
        ("I like you 오늘", "mixed"),
        ("사랑해 baby", "mixed"),
        ("오늘 날씨가 좋다 nice day", "mixed"),
    ],
)
def test_mixed_language_variants(text, expected):
    assert detect_language(text) == expected
