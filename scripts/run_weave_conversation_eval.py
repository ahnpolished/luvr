#!/usr/bin/env python
"""Run the Luvr conversation eval workflow in Weave."""

from __future__ import annotations

import argparse
import importlib
import os
from collections.abc import Callable
from typing import Any

from src.eval_workflow import DEFAULT_CONVERSATION_EVAL_NAME, run_weave_conversation_eval


def load_predictor(path: str) -> Callable[[dict[str, Any]], Any]:
    module_name, separator, attribute_name = path.partition(":")
    if not separator or not module_name or not attribute_name:
        raise ValueError("Predictor must use module:function format")

    module = importlib.import_module(module_name)
    predictor = getattr(module, attribute_name)
    if not callable(predictor):
        raise TypeError(f"Predictor is not callable: {path}")

    return predictor


def parse_span_labels(values: list[str]) -> dict[str, str]:
    labels: dict[str, str] = {}
    for value in values:
        key, separator, label_value = value.partition("=")
        if not separator or not key:
            raise ValueError("Span labels must use key=value format")
        labels[key] = label_value
    return labels


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project",
        default=os.getenv("WANDB_PROJECT"),
        help="Weave project, for example 'entity/luvr'. Defaults to WANDB_PROJECT.",
    )
    parser.add_argument("--eval-name", default=DEFAULT_CONVERSATION_EVAL_NAME)
    parser.add_argument(
        "--predictor",
        required=True,
        help="Callable to evaluate in module:function format.",
    )
    parser.add_argument(
        "--span-label",
        action="append",
        default=[],
        help="Span label in key=value format. Repeat to add multiple labels.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.project:
        raise SystemExit("--project or WANDB_PROJECT is required")

    run_weave_conversation_eval(
        predict=load_predictor(args.predictor),
        project=args.project,
        eval_name=args.eval_name,
        span_labels=parse_span_labels(args.span_label),
    )


if __name__ == "__main__":
    main()
