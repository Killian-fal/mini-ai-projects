from enum import Enum

from dspy.experimental import Choice, Noul, Score

from interactive_support_flow_api._internal import InternalError
from interactive_support_flow_api.tools.llm.model import (
    YesNoResult,
    ChoiceResult,
    ScoreResult,
)


def yes_no_result(answer: Noul) -> YesNoResult:
    if answer.probability is None:
        raise InternalError("LLM_MISSING_PROBABILITY")

    return YesNoResult(
        value=answer.value,
        confidence=answer.confidence,
        true_probability=answer.probability,
    )


def choice_result[E: Enum](answer: Choice, choices: type[E]) -> ChoiceResult[E]:
    if answer.probabilities is None:
        raise InternalError("LLM_MISSING_PROBABILITY")

    if not isinstance(answer.value, str):
        raise InternalError("LLM_INVALID_ANSWER_TYPE")

    return ChoiceResult(
        value=choices[answer.value],
        confidence=answer.confidence,
        probabilities={choices[label]: p for label, p in answer.probabilities.items()},
    )


def score_result[E: Enum](answer: Score, levels: type[E]) -> ScoreResult[E]:
    if answer.probabilities is None or answer.level is None:
        raise InternalError("LLM_MISSING_PROBABILITY")

    members = list(levels)
    return ScoreResult(
        value=answer.value,
        level=members[answer.level],
        confidence=answer.confidence,
        probabilities={
            level: answer.probabilities[i] for i, level in enumerate(levels)
        },
    )
