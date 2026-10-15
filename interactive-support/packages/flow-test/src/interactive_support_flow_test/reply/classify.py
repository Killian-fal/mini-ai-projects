from collections.abc import Mapping
from enum import Enum
from typing import overload

from interactive_support_flow_api.tools.llm import (
    ChoiceResult,
    ScoreResult,
    YesNoResult,
)
from interactive_support_flow_test.reply.model import Answer, ClassifyReply


def classify(given: Mapping[str, str], *answers: Answer) -> ClassifyReply:
    """
    One `llm.classify(**given)...run()`: one answer per question, in the order of the questions.
    """
    return ClassifyReply(given, answers)


@overload
def yes_no(question: str, value: bool) -> Answer: ...
@overload
def yes_no(
    question: str, value: bool, *, confidence: float, true_probability: float
) -> Answer: ...
def yes_no(
    question: str,
    value: bool,
    *,
    confidence: float | None = None,
    true_probability: float | None = None,
) -> Answer:
    """
    `value` alone when the LLM is certain. Otherwise the confidence and the probability of True, given by the LLM.
    """
    result = YesNoResult(
        value=value,
        confidence=1.0 if confidence is None else confidence,
        true_probability=float(value) if true_probability is None else true_probability,
    )
    return Answer(question, result)


@overload
def choose(question: str, value: Enum) -> Answer: ...
@overload
def choose[E: Enum](
    question: str, value: E, *, confidence: float, probabilities: Mapping[E, float]
) -> Answer: ...
def choose[E: Enum](
    question: str,
    value: E,
    *,
    confidence: float | None = None,
    probabilities: Mapping[E, float] | None = None,
) -> Answer:
    """
    `value` alone when the LLM is certain. Otherwise the confidence and the probability of every member, given by the LLM.
    """
    choices = type(value)
    result = ChoiceResult(
        value=value,
        confidence=1.0 if confidence is None else confidence,
        probabilities=_probabilities(choices, value, probabilities),
    )
    return Answer(question, result)


@overload
def score(question: str, level: Enum) -> Answer: ...
@overload
def score[E: Enum](
    question: str,
    level: E,
    *,
    value: float,
    confidence: float,
    probabilities: Mapping[E, float],
) -> Answer: ...
def score[E: Enum](
    question: str,
    level: E,
    *,
    value: float | None = None,
    confidence: float | None = None,
    probabilities: Mapping[E, float] | None = None,
) -> Answer:
    """
    `level` alone when the LLM is certain. Otherwise the continuous value, the confidence and the probability of every member.
    """
    levels = type(level)
    result = ScoreResult(
        value=list(levels).index(level) if value is None else value,
        level=level,
        confidence=1.0 if confidence is None else confidence,
        probabilities=_probabilities(levels, level, probabilities),
    )
    return Answer(question, result)


def _probabilities[E: Enum](
    members: type[E], certain: E, probabilities: Mapping[E, float] | None
) -> dict[E, float]:
    if probabilities is None:
        return {member: float(member is certain) for member in members}
    if set(probabilities) != set(members):
        raise AssertionError(
            f"LLM_REPLY_INCOMPLETE:{members.__name__}"
        )  # every member, and only them
    return dict(probabilities)
