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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.project:
        raise SystemExit("--project or WANDB_PROJECT is required")

    run_weave_conversation_eval(
        predict=load_predictor(args.predictor),
        project=args.project,
        eval_name=args.eval_name,
    )


if __name__ == "__main__":
    main()
