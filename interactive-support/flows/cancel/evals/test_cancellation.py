"""
The LLM calls of cancellation.py, on the reasons a customer gives to cancel: `cancellation/`, one file per kind of
reason, `expected` saying whether it is a service issue.
"""

import re
import tomllib
from pathlib import Path

import pytest
from pydantic import BaseModel

from interactive_support_flow_api.model.context import FlowContext, Issue, Language
from interactive_support_flow_api.model.message import Bucket, GeneratedText, TextCode
from interactive_support_flow_cancel.cancellation import (
    CancelReason,
    apologize,
    is_service_issue,
)
from interactive_support_flow_eval import Case, evaluate

_APOLOGY = re.compile(r"désolé|excus|pardon|regrett|navré", re.IGNORECASE)
_CANCELLED = re.compile(r"\bannulée?s?\b", re.IGNORECASE)


class Group(BaseModel):
    expected: bool
    inputs: list[str]


class Said(Bucket):
    def __init__(self) -> None:
        self.messages: list[TextCode | GeneratedText] = []

    def add_code(self, code: TextCode) -> None:
        self.messages.append(code)

    def add_generated(self, text: GeneratedText) -> None:
        self.messages.append(text)


def read_cases(folder: Path) -> list[Case[str, bool]]:
    cases: list[Case[str, bool]] = []
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


def given_reason(reason: str) -> FlowContext:
    ctx = FlowContext(issue=Issue.CANCEL, order_number="#CMA_001", language=Language.FR)
    ctx.set_extension(CancelReason(text=reason))
    return ctx


def write_apology(reason: str) -> str:
    said = Said()
    apologize(given_reason(reason), said)
    match said.messages:
        case [GeneratedText(text=text)]:
            return text
        case messages:
            raise AssertionError(f"EVAL_UNEXPECTED_MESSAGES:{messages}")


@pytest.mark.eval
def test_is_service_issue(request: pytest.FixtureRequest):
    evaluate(
        "cancel.is_service_issue",
        read_cases(request.path.parent / "cancellation"),
        run=lambda reason: is_service_issue(given_reason(reason), Said()),
        criteria={"service_issue": lambda answer, expected: answer is expected},
    )


@pytest.mark.eval
def test_apologize(request: pytest.FixtureRequest):
    """
    Only on the service issues: the flow apologizes for nothing else.
    """
    # TODO: evolution possible ici, nouveau cas : LLM as a judge
    evaluate(
        "cancel.apologize",
        [
            Case(input=case.input, expected=None, group=case.group)
            for case in read_cases(request.path.parent / "cancellation")
            if case.expected
        ],
        run=write_apology,
        criteria={
            "apologizes": lambda text, _: _APOLOGY.search(text) is not None,
            "asks_nothing": lambda text, _: "?" not in text,
            "doesnt_say_cancelled": lambda text, _: _CANCELLED.search(text) is None,
        },
    )
