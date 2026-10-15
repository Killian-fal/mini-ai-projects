from collections.abc import Callable
from enum import Enum
from typing import Any, NamedTuple

import dspy
from dspy.experimental import Choice, Noul, Score

from interactive_support_flow_api.tools.llm.model import (
    YesNoResult,
    ScoreResult,
    ChoiceResult,
)
from interactive_support_flow_api.tools.llm.result import (
    yes_no_result,
    choice_result,
    score_result,
)
from interactive_support_flow_api._internal import JEV_CLIENT


type _Decision = type[Noul] | type[Choice] | type[Score]


class _Question(NamedTuple):
    kind: _Decision
    text: str
    decode: Callable[[Any], Any]


class Classify[*Results]:
    """
    Questions ask to a Decision Model.
    Build it with `classify(...)`, chain the questions, then call `run()`.
    """

    def __init__(self, inputs: dict[str, str], questions: list[_Question]):
        self._inputs = inputs
        self._questions = questions

    def yes_no(
        self, question: str, *, yes: str, no: str
    ) -> "Classify[*Results, YesNoResult]":
        """
        Adds a yes/no question.
        `yes` and `no` describe precisely when the answer is True and when it is False.
        """
        return self._add(
            Noul[(True, yes), (False, no)],
            question,
            lambda answer: yes_no_result(answer),
        )

    def choose[E: Enum](
        self, question: str, choices: type[E]
    ) -> "Classify[*Results, ChoiceResult[E]]":
        """
        Adds a question whose answer is one member of `choices`.
        Each value of the enum is the description sent.
        """
        decision = Choice[tuple((choice.name, choice.value) for choice in choices)]
        return self._add(
            decision, question, lambda answer: choice_result(answer, choices)
        )

    def score[E: Enum](
        self, question: str, levels: type[E]
    ) -> "Classify[*Results, ScoreResult[E]]":
        """
        Adds a question whose answer is a position on the scale `levels`.
        Members go in increasing order (2 to 10 of them), each member enum's value is its description.
        """
        decision = Score[tuple(level.value for level in levels)]
        return self._add(
            decision, question, lambda answer: score_result(answer, levels)
        )

    def run(self) -> tuple[*Results]:
        """
        Asks every question in a single call. Results come back in the order the questions were added.
        """
        fields = {name: (str, dspy.InputField()) for name in self._inputs}
        for i, (kind, question, _) in enumerate(self._questions):
            fields[f"answer_{i}"] = (kind, dspy.OutputField(desc=question))

        predict = dspy.Predict(dspy.make_signature(fields))
        predict.set_lm(JEV_CLIENT)
        prediction = predict(**self._inputs)

        return tuple(
            decode(prediction[f"answer_{i}"])
            for i, (_, _, decode) in enumerate(self._questions)
        )

    def _add[NewResult](
        self, kind: _Decision, question: str, decode: Callable[[Any], NewResult]
    ) -> "Classify[*Results, NewResult]":
        return Classify(
            self._inputs, [*self._questions, _Question(kind, question, decode)]
        )


def classify(**kwargs: str) -> Classify[()]:
    """
    Starts a set of questions about the given inputs.
    Each keyword is an input of the Decision Model: its name is the label the Decision Model sees, so make it meaningful.
    """
    return Classify(kwargs, questions=[])
