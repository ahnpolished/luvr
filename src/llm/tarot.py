"""Minimal v0.1.0 tarot card deck and prompt builder.

Provides 22 Major Arcana cards with English and Korean names plus a
language-aware prompt template for the LLM reading.
"""

from __future__ import annotations

MAJOR_ARCANA: list[dict[str, str]] = [
    {"id": "0", "name_en": "The Fool", "name_ko": "바보 (The Fool)"},
    {"id": "1", "name_en": "The Magician", "name_ko": "마법사 (The Magician)"},
    {"id": "2", "name_en": "The High Priestess", "name_ko": "여사제 (The High Priestess)"},
    {"id": "3", "name_en": "The Empress", "name_ko": "여제 (The Empress)"},
    {"id": "4", "name_en": "The Emperor", "name_ko": "황제 (The Emperor)"},
    {"id": "5", "name_en": "The Hierophant", "name_ko": "교황 (The Hierophant)"},
    {"id": "6", "name_en": "The Lovers", "name_ko": "연인 (The Lovers)"},
    {"id": "7", "name_en": "The Chariot", "name_ko": "전차 (The Chariot)"},
    {"id": "8", "name_en": "Strength", "name_ko": "힘 (Strength)"},
    {"id": "9", "name_en": "The Hermit", "name_ko": "은둔자 (The Hermit)"},
    {"id": "10", "name_en": "Wheel of Fortune", "name_ko": "운명의 수레바퀴 (Wheel of Fortune)"},
    {"id": "11", "name_en": "Justice", "name_ko": "정의 (Justice)"},
    {"id": "12", "name_en": "The Hanged Man", "name_ko": "매달린 남자 (The Hanged Man)"},
    {"id": "13", "name_en": "Death", "name_ko": "죽음 (Death)"},
    {"id": "14", "name_en": "Temperance", "name_ko": "절제 (Temperance)"},
    {"id": "15", "name_en": "The Devil", "name_ko": "악마 (The Devil)"},
    {"id": "16", "name_en": "The Tower", "name_ko": "탑 (The Tower)"},
    {"id": "17", "name_en": "The Star", "name_ko": "별 (The Star)"},
    {"id": "18", "name_en": "The Moon", "name_ko": "달 (The Moon)"},
    {"id": "19", "name_en": "The Sun", "name_ko": "태양 (The Sun)"},
    {"id": "20", "name_en": "Judgement", "name_ko": "심판 (Judgement)"},
    {"id": "21", "name_en": "The World", "name_ko": "세계 (The World)"},
]


def build_tarot_prompt(selected_cards: list[str], *, user_language: str = "en") -> str:
    """Build a system prompt for the tarot reading LLM call."""
    cards_formatted = "\n".join(f"- {name}" for name in selected_cards)

    lang_instruction = ""
    if user_language == "ko":
        lang_instruction = "\nYou MUST write the entire reading in Korean (한국어). Use natural, warm Korean."
    elif user_language == "mixed":
        lang_instruction = "\nMatch the user's language mix naturally."
    else:
        lang_instruction = "\nWrite the reading in warm, conversational English."

    return f"""You are Luvr's tarot reader — a warm, mystical guide who interprets
3-card spreads through a dating and relationships lens.

## Important
- This is reflective entertainment. Never claim to predict the future or diagnose health/financial/life-critical issues.
- Keep the reading warm, encouraging, and honest — like a close friend sharing insight.
- Do NOT mention payment, prices, Stripe, or upgrades. This is a free alpha feature.

## Selected Cards
{cards_formatted}

## Spread Positions
1. Situation — where the user is now
2. Challenge — what's holding them back or creating tension
3. Advice — what the user can do or focus on

Give a cohesive reading that connects all three cards into one narrative.{lang_instruction}
"""
