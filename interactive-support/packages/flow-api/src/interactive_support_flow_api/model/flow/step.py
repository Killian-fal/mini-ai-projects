from collections.abc import Callable
from enum import Enum, StrEnum
from typing import Any

from pydantic import BaseModel

from interactive_support_flow_api.model.context import FlowContext
from interactive_support_flow_api.model.question import Question
from interactive_support_flow_api.model.message import Bucket


class StepId(StrEnum):
    """
    Empty base: each flow extends it with its own step ids.
    """


class End(Enum):
    END = "END"


END = End.END


def forward[T](ctx: FlowContext, answer: T, bucket: Bucket) -> T:
    return answer


class Step(BaseModel):
    id: StepId
    pre_hook: Callable[[FlowContext, Bucket], None] | None = None
    run: Callable[[FlowContext, Bucket], Any]
    next: StepId | End | dict[Any, StepId | End]


class AskStep[T](BaseModel):
    id: StepId
    pre_hook: Callable[[FlowContext, Bucket], None] | None = None
    question: Callable[[FlowContext], Question[T]]
    run: Callable[[FlowContext, T, Bucket], Any] = forward
    next: StepId | End | dict[Any, StepId | End]
