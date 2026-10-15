import tomllib
from pathlib import Path

import pytest
from pydantic import BaseModel

from interactive_support_core.opening.detection import (
    detect_first_message,
    detect_issue,
)
from interactive_support_flow_api.model.context import Issue, Language
from interactive_support_flow_eval import Case, evaluate


class Group(BaseModel):
    expected: frozenset[Issue]
    inputs: list[str]


def read_cases(folder: Path) -> list[Case[str, frozenset[Issue]]]:
    cases: list[Case[str, frozenset[Issue]]] = []
    for path in sorted(folder.glob("*.toml")):
        try:
            group = Group.model_validate(tomllib.loads(path.read_text()))
        except Exception as error:
            raise AssertionError(f"EVAL_CASE_INVALID:{path.name}:{error}") from None

        cases.extend(
            [
                Case(input=input, expected=group.expected, group=path.stem)
                for input in group.inputs
            ]
        )

    return cases


@pytest.mark.eval
def test_first_message(request: pytest.FixtureRequest):
    evaluate(
        "routing.first_message",
        read_cases(request.path.parent / "routing"),
        run=detect_first_message,
        criteria={
            "language": lambda detected, _: detected[0] is Language.FR,
            "issues": lambda detected, expected: (
                {c.value for c in detected[1]} == expected
            ),
        },
    )


@pytest.mark.eval
def test_issue_described_again(request: pytest.FixtureRequest):
    evaluate(
        "routing.issue_described_again",
        read_cases(request.path.parent / "routing"),
        run=detect_issue,
        criteria={
            "issues": lambda candidates, expected: (
                {c.value for c in candidates} == expected
            )
        },
    )
