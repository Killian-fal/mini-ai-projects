from enum import Enum
from types import NoneType, UnionType
from typing import Any, Union, get_args, get_origin, get_type_hints

from interactive_support_flow_api.model.flow import Flow, Step, AskStep, StepId
from interactive_support_flow_api.model.flow.step import forward


def check_flow(flow: Flow):
    """
    The structure of a flow, whatever the path a test takes: each flow calls it in its tests.
    A `next` dict needs a `run` annotated with what it returns (bool, an Enum, `| None`): every value must lead somewhere.
    With `forward`, the value is the answer: FlowTest checks it against the question when it is asked.
    """
    issue = flow.issue.value
    ids = [step.id for step in flow.steps]
    if duplicated := sorted(
        {step_id.name for step_id in ids if ids.count(step_id) > 1}
    ):
        raise AssertionError(f"FLOW_STEP_DUPLICATED:{issue}:{','.join(duplicated)}")

    steps = {step.id: step for step in flow.steps}
    for step in flow.steps:
        if unknown := sorted(
            target.name for target in _targets(step) if target not in steps
        ):
            raise AssertionError(
                f"FLOW_NEXT_UNKNOWN:{issue}:{step.id.name}:{','.join(unknown)}"
            )

        if isinstance(step.next, dict) and step.run is not forward:
            expected = _returned_values(step.run)
            if expected is None:
                raise AssertionError(f"FLOW_NEXT_UNTYPED:{issue}:{step.id.name}")
            if set(step.next) != expected:
                missing, extra = (
                    sorted(map(str, expected - set(step.next))),
                    sorted(map(str, set(step.next) - expected)),
                )
                raise AssertionError(
                    f"FLOW_NEXT_NOT_EXHAUSTIVE:{issue}:{step.id.name}:missing={','.join(missing)}:extra={','.join(extra)}"
                )

    reachable, todo = set[StepId](), [flow.steps[0].id]
    while todo:
        if (step_id := todo.pop()) not in reachable:
            reachable.add(step_id)
            todo.extend(_targets(steps[step_id]))
    if unreachable := sorted(
        step_id.name for step_id in ids if step_id not in reachable
    ):
        raise AssertionError(f"FLOW_STEP_UNREACHABLE:{issue}:{','.join(unreachable)}")

    # steps that never ask: a cycle among them runs forever. Peel off the ones leading out of it until nothing moves
    plain = {
        step.id: {
            target for target in _targets(step) if isinstance(steps[target], Step)
        }
        for step in flow.steps
        if isinstance(step, Step)
    }
    while leaves := [
        step_id for step_id, targets in plain.items() if not targets & plain.keys()
    ]:
        for step_id in leaves:
            del plain[step_id]
    if plain:
        raise AssertionError(
            f"FLOW_LOOP_WITHOUT_ASK:{issue}:{','.join(sorted(step_id.name for step_id in plain))}"
        )


def _targets(step: Step | AskStep[Any]) -> list[StepId]:
    targets = step.next.values() if isinstance(step.next, dict) else [step.next]
    return [target for target in targets if isinstance(target, StepId)]


def _returned_values(run: Any) -> set[Any] | None:
    """
    Every value `run` can return according to its annotation, None when it can't be known.
    """
    try:
        returned = get_type_hints(run).get("return")
    except TypeError:
        return None  # not a function (a partial...)
    return None if returned is None else _values(returned)


def _values(annotation: Any) -> set[Any] | None:
    if get_origin(annotation) in (Union, UnionType):
        parts = [_values(arg) for arg in get_args(annotation)]
        return (
            None
            if None in parts
            else set[Any]().union(*(part for part in parts if part is not None))
        )
    if annotation is bool:
        return {True, False}
    if annotation is NoneType:
        return {None}
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        return set(annotation)
    return None
