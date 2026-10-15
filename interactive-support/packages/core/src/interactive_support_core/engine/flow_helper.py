from typing import Any

from interactive_support_flow_api._internal import InternalError
from interactive_support_flow_api.model.flow import Flow, StepId, Step, AskStep, End
from interactive_support_flow_api.model.context import Issue
from interactive_support_core.registry import FLOWS


def find_flow(issue: Issue) -> Flow:
    flow = FLOWS.get(issue)
    if flow is None:
        raise InternalError(f"FLOW_NOT_FOUND:{issue.value}")
    return flow


def find_step(flow: Flow, step_id: StepId) -> Step | AskStep[Any]:
    for step in flow.steps:
        if step.id == step_id:
            return step
    raise InternalError(f"STEP_NOT_FOUND:{step_id.name}")


def find_ask_step(flow: Flow, action_id: str) -> AskStep[Any]:
    for step in flow.steps:
        if isinstance(step, AskStep) and flow.action_id(step.id) == action_id:
            return step
    raise InternalError(f"STEP_NOT_FOUND:{action_id}")


def determine_next_step(step: Step | AskStep[Any], value: Any) -> StepId | End:
    if not isinstance(step.next, dict):
        return step.next

    if value not in step.next:
        raise InternalError(f"NEXT_NOT_FOUND:{step.id.name}:{value}")
    return step.next[value]
