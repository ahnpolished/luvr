import subprocess
import sys

from src.proactive import ManualCheckinInput, build_manual_checkin


def test_manual_checkin_uses_name_and_context_without_news_or_content() -> None:
    message = build_manual_checkin(ManualCheckinInput(display_name="Tae", context="last night's date"))

    assert message == (
        "Hey Tae, quick check-in. Still thinking about last night's date. "
        "Want to talk through what happened, or should I help you draft the next text?"
    )
    assert "news" not in message.lower()
    assert "article" not in message.lower()


def test_manual_checkin_handles_missing_optional_context() -> None:
    assert build_manual_checkin(ManualCheckinInput()) == (
        "Hey, quick check-in. " "Want to talk through what happened, or should I help you draft the next text?"
    )


def test_manual_checkin_script_prints_only_message() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/manual_proactive_checkin.py",
            "--display-name",
            "Tae",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip() == (
        "Hey Tae, quick check-in. " "Want to talk through what happened, or should I help you draft the next text?"
    )
    assert result.stderr == ""
