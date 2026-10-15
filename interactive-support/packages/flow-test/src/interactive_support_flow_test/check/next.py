from typing import Any

from interactive_support_flow_api.model.flow import AskStep
from interactive_support_flow_api.model.flow.step import forward
from interactive_support_flow_test.model import Choice, Confirm, Next


def check_next_covers(step: AskStep[Any], asked: Next):
    """
    With `forward`, the answer itself picks the next step: every answer proposed must lead somewhere.
    """
    if step.run is not forward or not isinstance(step.next, dict):
        return

    match asked:
        case Choice():
            answers: list[Any] = list(asked.options)
        case Confirm():
            answers = [True, False]
        case _:
            return

    if missing := [answer for answer in answers if answer not in step.next]:
        raise AssertionError(
            f"NEXT_MISSING_OPTION:{step.id.name}:{','.join(map(str, missing))}"
        )
