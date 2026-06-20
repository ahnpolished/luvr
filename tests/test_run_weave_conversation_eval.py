import pytest

from scripts.run_weave_conversation_eval import load_predictor


def test_load_predictor_requires_module_function_format() -> None:
    with pytest.raises(ValueError, match="module:function"):
        load_predictor("src.eval_workflow")


def test_load_predictor_requires_callable() -> None:
    with pytest.raises(TypeError, match="not callable"):
        load_predictor("src.eval_workflow:DEFAULT_CONVERSATION_EVAL_NAME")


def test_load_predictor_returns_callable() -> None:
    predictor = load_predictor("src.eval_workflow:build_conversation_eval_cases")

    assert callable(predictor)
