from enum import auto

import pytest

from interactive_support_core.registry import FLOWS
from interactive_support_flow_api.model.context import FlowContext, Issue, Language
from interactive_support_flow_api.model.flow import END, AskStep, Flow, StepId
from interactive_support_flow_api.model.message import Bucket, TextCode
from interactive_support_flow_api.model.question import (
    ChoiceQuestion,
    FormQuestion,
    TextQuestion,
)
from interactive_support_flow_api.tools import llm
from interactive_support_flow_test import Choice, FlowTest, Form, Text, reply


class ProbeStep(StepId):
    PICK = auto()
    REASON = auto()
    ADDRESS = auto()


class ProbeCode(TextCode):
    ASK_PICK = auto()
    URGENT = auto()
    NOT_URGENT = auto()
    FILLED = auto()


class ProbeField(TextCode):
    STREET = auto()
    CITY = auto()


class ProbeChoice(TextCode):
    PROPOSED = auto()
    NEVER_PROPOSED = auto()


URGENT_QUESTION = "Is it urgent?"


def answer_urgency(ctx: FlowContext, reason: str, bucket: Bucket) -> None:
    (urgent,) = (
        llm.classify(reason=reason)
        .yes_no(URGENT_QUESTION, yes="It must be done today", no="It can wait")
        .run()
    )
    bucket.add_code(ProbeCode.URGENT if urgent.value else ProbeCode.NOT_URGENT)


# the probe flow takes the place of CANCEL in the registry, for each test
PROBE_FLOW = Flow(
    issue=Issue.CANCEL,
    description="probe",
    steps=[
        AskStep(
            id=ProbeStep.PICK,
            pre_hook=lambda ctx, bucket: bucket.add_code(ProbeCode.ASK_PICK),
            question=lambda ctx: ChoiceQuestion(options=[ProbeChoice.PROPOSED]),
            next={ProbeChoice.PROPOSED: ProbeStep.REASON},
        ),
        AskStep(
            id=ProbeStep.REASON,
            question=lambda ctx: TextQuestion(),
            run=answer_urgency,
            next=END,
        ),
    ],
)


@pytest.fixture(autouse=True)
def _registered(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(FLOWS, Issue.CANCEL, PROBE_FLOW)


def start() -> FlowTest[Choice[ProbeChoice]]:
    return FlowTest(
        PROBE_FLOW,
        order_number="#PROBE",
        language=Language.FR,
        said=[ProbeCode.ASK_PICK],
        next=Choice(ProbeStep.PICK, [ProbeChoice.PROPOSED]),
    )


def at_reason() -> FlowTest[Text]:
    return start().choose(ProbeChoice.PROPOSED, said=[], next=Text(ProbeStep.REASON))


def test_a_right_test_passes():
    at_reason().write(
        "Avant ce soir",
        llm=[
            reply.classify(
                {"reason": "Avant ce soir"}, reply.yes_no(URGENT_QUESTION, True)
            )
        ],
        said=[ProbeCode.URGENT],
        next=END,
    )


def test_flow_not_registered(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delitem(FLOWS, Issue.CANCEL)

    with pytest.raises(AssertionError, match="FLOW_NOT_REGISTERED:CANCEL"):
        start()


def test_turn_mismatch():
    with pytest.raises(AssertionError, match="TURN_MISMATCH"):
        FlowTest(
            PROBE_FLOW,
            order_number="#PROBE",
            language=Language.FR,
            said=[],
            next=Choice(ProbeStep.PICK, [ProbeChoice.PROPOSED]),
        )


def test_unscripted_llm_call():
    with pytest.raises(AssertionError, match="UNSCRIPTED_LLM_CALL"):
        at_reason().write("Avant ce soir", said=[ProbeCode.URGENT], next=END)


def test_unused_llm_reply():
    with pytest.raises(AssertionError, match="UNUSED_LLM_REPLY"):
        start().choose(
            ProbeChoice.PROPOSED,
            llm=[
                reply.classify(
                    {"reason": "Avant ce soir"}, reply.yes_no(URGENT_QUESTION, True)
                )
            ],
            said=[],
            next=Text(ProbeStep.REASON),
        )


def test_llm_receives_something_else():
    with pytest.raises(AssertionError, match="LLM_CALL_MISMATCH"):
        at_reason().write(
            "Avant ce soir",
            llm=[
                reply.classify(
                    {"reason": "Quand vous pouvez"}, reply.yes_no(URGENT_QUESTION, True)
                )
            ],
            said=[ProbeCode.URGENT],
            next=END,
        )


def test_llm_asked_another_question():
    with pytest.raises(AssertionError, match="LLM_CALL_MISMATCH"):
        at_reason().write(
            "Avant ce soir",
            llm=[
                reply.classify(
                    {"reason": "Avant ce soir"}, reply.yes_no("Is it important?", True)
                )
            ],
            said=[ProbeCode.URGENT],
            next=END,
        )


def test_option_not_proposed():
    with pytest.raises(AssertionError, match="ANSWER_MISMATCH"):
        start().choose(ProbeChoice.NEVER_PROPOSED, said=[], next=END)


def test_proposed_option_missing_from_next(monkeypatch: pytest.MonkeyPatch):
    broken = Flow(
        issue=Issue.CANCEL,
        description="NEVER_PROPOSED leads nowhere",
        steps=[
            AskStep(
                id=ProbeStep.PICK,
                question=lambda ctx: ChoiceQuestion(options=list(ProbeChoice)),
                next={ProbeChoice.PROPOSED: END},
            ),
        ],
    )
    monkeypatch.setitem(FLOWS, Issue.CANCEL, broken)

    with pytest.raises(AssertionError, match="NEXT_MISSING_OPTION:PICK"):
        FlowTest(
            broken,
            order_number="#PROBE",
            language=Language.FR,
            said=[],
            next=Choice(ProbeStep.PICK, list(ProbeChoice)),
        )


FORM_FLOW = Flow(
    issue=Issue.CANCEL,
    description="a form, the city pre-filled",
    steps=[
        AskStep(
            id=ProbeStep.ADDRESS,
            question=lambda ctx: FormQuestion(
                fields=list(ProbeField),
                values={ProbeField.STREET: None, ProbeField.CITY: "Lyon"},
            ),
            run=lambda ctx, address, bucket: bucket.add_code(ProbeCode.FILLED),
            next=END,
        ),
    ],
)


def at_form(monkeypatch: pytest.MonkeyPatch) -> FlowTest[Form[ProbeField]]:
    monkeypatch.setitem(FLOWS, Issue.CANCEL, FORM_FLOW)
    return FlowTest(
        FORM_FLOW,
        order_number="#PROBE",
        language=Language.FR,
        said=[],
        next=Form(ProbeStep.ADDRESS, list(ProbeField), {ProbeField.CITY: "Lyon"}),
    )


def test_a_form_is_sent_with_every_field(monkeypatch: pytest.MonkeyPatch):
    at_form(monkeypatch).fill(
        {ProbeField.STREET: "5 rue Mercière", ProbeField.CITY: "Lyon"},
        said=[ProbeCode.FILLED],
        next=END,
    )


def test_a_form_without_every_field(monkeypatch: pytest.MonkeyPatch):
    with pytest.raises(AssertionError, match="ANSWER_MISMATCH"):
        at_form(monkeypatch).fill(
            {ProbeField.STREET: "5 rue Mercière"}, said=[ProbeCode.FILLED], next=END
        )
