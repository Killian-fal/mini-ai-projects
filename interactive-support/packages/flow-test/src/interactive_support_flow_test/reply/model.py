from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from interactive_support_flow_api.tools.llm import (
    ChoiceResult,
    GenerateInput,
    GenerateOutput,
    ScoreResult,
    YesNoResult,
)


@dataclass(frozen=True)
class Answer:
    """
    The answer to one question of a classify call. Built by `yes_no`, `choose` or `score`.
    `question` is the constant the flow declares for its question.
    """

    question: str
    result: YesNoResult | ChoiceResult[Any] | ScoreResult[Any]


@dataclass(frozen=True)
class ClassifyReply:
    given: Mapping[str, str]
    answers: tuple[Answer, ...]


@dataclass(frozen=True)
class GenerateReply:
    given: GenerateInput
    output: GenerateOutput


type Reply = ClassifyReply | GenerateReply
