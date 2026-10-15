import pytest

from interactive_support_flow_eval import Case, evaluate


def test_an_eval_without_cases():
    with pytest.raises(AssertionError, match="EVAL_WITHOUT_CASES"):
        evaluate(
            "eval",
            list[Case[str, str]](),
            run=str.upper,
            criteria={"upper": lambda output, expected: output == expected},
        )


def test_an_eval_without_criteria():
    with pytest.raises(AssertionError, match="EVAL_WITHOUT_CRITERIA"):
        evaluate(
            "eval",
            [Case(input="annuler", expected="ANNULER", group="upper")],
            run=str.upper,
            criteria={},
        )
