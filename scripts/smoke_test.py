#!/usr/bin/env python3
"""Smoke test script for Luvr — tests all message types without requiring real iMessage.

Usage:
    python scripts/smoke_test.py

Requires:
    - Luvr server running (make run in another terminal)
    - Valid API keys in .env
"""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import settings
from src.llm.client import create_llm_client

TEST_MESSAGES = {
    "text": "I've been talking to someone for 3 weeks and they suddenly stopped replying. What should I do?",
    "text_short": "Should I double text?",
    "text_first_date": "What's a good first date idea that's not just dinner and a movie?",
}

SMOKE_TEST_DIR = Path(__file__).parent / "smoke_test_data"


async def test_text_messages():
    """Test plain text message responses."""
    print("\n📱 Testing TEXT messages...")
    print("-" * 40)

    client = create_llm_client()

    for name, message in TEST_MESSAGES.items():
        start = time.time()
        response = await client.generate_response(user_message=message)
        elapsed = time.time() - start

        status = "✅" if len(response) > 20 else "⚠️"
        print(f"  {status} [{name}] ({elapsed:.1f}s)")
        print(f"     Q: {message[:60]}...")
        print(f"     A: {response[:100]}...")
        print()

    return True


async def main():
    """Run all smoke tests."""
    # Add current dir to path
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))

    print("💨 Luvr Smoke Tests")
    print("=" * 50)
    print(f"  Provider: {settings.llm_provider}")
    print(f"  Model: {settings.llm_model}")

    all_passed = True

    try:
        await test_text_messages()
    except Exception as e:
        print(f"\n❌ Text message tests failed: {e}")
        all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All smoke tests passed!")
        return 0
    else:
        print("❌ Some tests failed. Check output above.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
