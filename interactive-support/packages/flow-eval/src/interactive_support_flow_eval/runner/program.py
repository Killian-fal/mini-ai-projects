from collections.abc import Callable, Mapping, Sequence
from typing import Any

import dspy
from pydantic_core import to_json

from interactive_support_flow_eval.model import Case


class Program[Input, Expected, Output](dspy.Module):
    def __init__(
        self,
        cases: Sequence[Case[Input, Expected]],
        run: Callable[[Input], Output],
        criteria: Mapping[str, Callable[[Output, Expected], bool]],
    ):
        super().__init__()
        self._cases = cases
        self._run = run
        self._criteria = criteria

    def forward(self, index: int) -> dspy.Prediction:
        case = self._cases[index]
        try:
            output = self._run(case.input)
            failed_criteria = [
                name
                for name, check in self._criteria.items()
                if not check(output, case.expected)
            ]
        except Exception as error:  # reported apart from the wrong answers
            return dspy.Prediction(
                output="", failed_criteria=[], error=f"{type(error).__name__}: {error}"
            )
        return dspy.Prediction(
            output=to_json(output, serialize_unknown=True).decode(),
            failed_criteria=failed_criteria,
            error=None,
        )


def passed(
    example: dspy.Example, prediction: dspy.Prediction, trace: Any = None
) -> bool:
    return prediction.error is None and not prediction.failed_criteria
