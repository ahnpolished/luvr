import pytest

from scripts.run_weave_conversation_eval import load_predictor, parse_span_labels


def test_load_predictor_requires_module_function_format() -> None:
    with pytest.raises(ValueError, match="module:function"):
        load_predictor("src.eval_workflow")


def test_load_predictor_requires_callable() -> None:
    with pytest.raises(TypeError, match="not callable"):
        load_predictor("src.eval_workflow:DEFAULT_CONVERSATION_EVAL_NAME")


def test_load_predictor_returns_callable() -> None:
    predictor = load_predictor("src.eval_workflow:build_conversation_eval_cases")

    assert callable(predictor)


def test_parse_span_labels() -> None:
    labels = parse_span_labels(["alpha_user_id=alpha_123", "display_name=Tae"])

    assert labels == {"alpha_user_id": "alpha_123", "display_name": "Tae"}


def test_parse_span_labels_requires_key_value_format() -> None:
    with pytest.raises(ValueError, match="key=value"):
        parse_span_labels(["display_name"])
