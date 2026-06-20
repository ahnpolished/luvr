#!/usr/bin/env python
"""Print a manual v0.1.0 proactive check-in message."""

from __future__ import annotations

import argparse

from src.proactive import ManualCheckinInput, build_manual_checkin


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--display-name")
    parser.add_argument("--context")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(
        build_manual_checkin(
            ManualCheckinInput(
                display_name=args.display_name,
                context=args.context,
            )
        )
    )


if __name__ == "__main__":
    main()
