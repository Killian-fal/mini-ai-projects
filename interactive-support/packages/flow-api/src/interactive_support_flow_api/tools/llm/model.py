from enum import Enum
from typing import Annotated

import dspy
from pydantic import BaseModel, ConfigDict, Field

Probability = Annotated[float, Field(ge=0, le=1)]


class YesNoResult(BaseModel):
    """
    Answer to a `yes_no` question.

    value: True when the `yes` description matches better than the `no` one (true_probability >= 0.5).
    """

    value: bool
    confidence: Probability
    true_probability: Probability


class ChoiceResult[E: Enum](BaseModel):
    """
    Answer to a `choose` question.
    """

    value: E
    confidence: Probability
    probabilities: dict[E, Probability]


class ScoreResult[E: Enum](BaseModel):
    """
    Answer to a `score` question.

    value: continuous score from 0 (first member) to len(levels) - 1 (last member), e.g. 1.4.
    level: the member of the enum closest to value.
    """

    value: float
    level: E
    confidence: Probability
    probabilities: dict[E, Probability]


Image = dspy.Image


class GenerateInput(BaseModel):
    """
    Base of the input given to `generate`.

    Each field is shown to the LLM: its name is the label, `Field(description=...)` says what it is.
    """


class GenerateOutput(BaseModel):
    """
    Base of the output returned by `generate`.

    Each field is what the LLM must produce, described with `Field(description=...)`.
    """

    model_config = ConfigDict(frozen=True)
