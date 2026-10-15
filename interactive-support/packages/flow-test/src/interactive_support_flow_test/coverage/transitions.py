from collections.abc import Generator
from contextlib import contextmanager
from enum import Enum
from typing import Any

import pytest

from interactive_support_core.engine import flow_helper, handler as engine
from interactive_support_core.registry import FLOWS
from interactive_support_flow_api.model.flow import AskStep, End, Flow, Step, StepId

_DIRECT = object()  # the key of a `next` that isn't a dict

# by identity: a test may run a broken copy of a flow under the same issue
_TESTED: list[Flow] = []
_TAKEN: set[tuple[int, StepId, Any]] = set()


def tested(flow: Flow):
    if not any(known is flow for known in _TESTED):
        _TESTED.append(flow)


@contextmanager
def recording() -> Generator[None]:
    """
    Records the transitions the engine takes inside: every transition goes through its `determine_next_step`.
    """
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(engine, "determine_next_step", _determine_and_record)
        yield


def _determine_and_record(step: Step | AskStep[Any], value: Any) -> StepId | End:
    target = flow_helper.determine_next_step(step, value)
    for flow in _TESTED:
        if any(candidate is step for candidate in flow.steps):
            _TAKEN.add(
                (
                    id(flow),
                    step.id,
                    value if isinstance(step.next, dict) else _DIRECT,
                )
            )
    return target


def missing() -> list[str]:
    """
    The transitions never taken, for the tested flows that are the installed ones.
    """
    result: list[str] = []
    for flow in _TESTED:
        if FLOWS.get(flow.issue) is not flow:
            continue
        for step in flow.steps:
            transitions = (
                step.next.items()
                if isinstance(step.next, dict)
                else [(_DIRECT, step.next)]
            )
            for key, target in transitions:
                if (id(flow), step.id, key) not in _TAKEN:
                    label = "" if key is _DIRECT else f"[{_show(key)}]"
                    result.append(
                        f"{flow.issue.value}.{step.id.name}{label} -> {_show(target)}"
                    )
    return result


def _show(value: Any) -> str:
    if isinstance(value, StepId | End):
        return value.name
    return (
        f"{type(value).__name__}.{value.name}"
        if isinstance(value, Enum)
        else repr(value)
    )
