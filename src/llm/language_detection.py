"""Lightweight language detection for v0.1.0 bilingual (English/Korean) support.

Uses character-range heuristics. Not a statistical NLP classifier — this is
intentionally simple for the alpha.
"""

from __future__ import annotations

import re

_KOREAN_CHAR_RE = re.compile(r"[\uAC00-\uD7AF]")  # 한글 syllables


def detect_language(text: str) -> str:
    """Return ``en``, ``ko``, or ``mixed`` for the best-fit language.

    Defaults to ``en`` when text contains no alphabetic or Hangul characters.
    """
    stripped = text.strip()
    if not stripped:
        return "en"

    has_korean = bool(_KOREAN_CHAR_RE.search(stripped))
    has_english = bool(re.search(r"[a-zA-Z]{2,}", stripped))

    if has_korean and has_english:
        return "mixed"
    if has_korean:
        return "ko"
    return "en"
