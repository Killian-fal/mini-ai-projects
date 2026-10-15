from enum import auto

import pytest

from interactive_support_flow_api.model.context import FlowContext, Issue
from interactive_support_flow_api.model.flow import END, Flow, Step, StepId
from interactive_support_flow_api.model.message import Bucket
from interactive_support_flow_test import check_flow


class S(StepId):
    A = auto()
    B = auto()


def nothing(ctx: FlowContext, bucket: Bucket) -> None:
    pass


def always(ctx: FlowContext, bucket: Bucket) -> bool:
    return True


def flow(*steps: Step) -> Flow:
    return Flow(issue=Issue.CANCEL, description="test", steps=list(steps))


@pytest.mark.parametrize(
    "broken, error",
    [
        pytest.param(
            flow(
                Step(id=S.A, run=nothing, next=END), Step(id=S.A, run=nothing, next=END)
            ),
            "FLOW_STEP_DUPLICATED:CANCEL:A",
            id="duplicated",
        ),
        pytest.param(
            flow(Step(id=S.A, run=nothing, next=S.B)),
            "FLOW_NEXT_UNKNOWN:CANCEL:A:B",
            id="unknown",
        ),
        pytest.param(
            flow(
                Step(id=S.A, run=lambda ctx, bucket: True, next={True: END, False: END})
            ),
            "FLOW_NEXT_UNTYPED:CANCEL:A",
            id="untyped",
        ),
        pytest.param(
            flow(Step(id=S.A, run=always, next={True: END})),
            "FLOW_NEXT_NOT_EXHAUSTIVE:CANCEL:A:missing=False:extra=",
            id="not exhaustive",
        ),
        pytest.param(
            flow(
                Step(id=S.A, run=nothing, next=END), Step(id=S.B, run=nothing, next=END)
            ),
            "FLOW_STEP_UNREACHABLE:CANCEL:B",
            id="unreachable",
        ),
        pytest.param(
            flow(
                Step(id=S.A, run=nothing, next=S.B), Step(id=S.B, run=nothing, next=S.A)
            ),
            "FLOW_LOOP_WITHOUT_ASK:CANCEL:A,B",
            id="loop",
        ),
    ],
)
def test_broken_flow(broken: Flow, error: str):
    with pytest.raises(AssertionError, match=f"^{error}$"):
        check_flow(broken)
