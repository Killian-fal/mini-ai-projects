import httpx2
from fastapi.testclient import TestClient

from interactive_support_api.app import app
from interactive_support_core.opening.code import OpeningCode
from interactive_support_core.opening.required_message_id import RequiredMessageId
from interactive_support_flow_test import fake_llm, reply

from .conftest import (
    ISSUE_CHOICE_ASKED,
    SURELY_CANCEL,
    Json,
    answer,
    get,
    transcript,
)

DESCRIPTION = "Je veux annuler la commande cma_001"


def answer_with_the_llm_down(asked: Json) -> httpx2.Response:
    return TestClient(app, raise_server_exceptions=False).post(
        f"/conversations/{asked['id']}/answers",
        json={"action_id": RequiredMessageId.ISSUE, "response": DESCRIPTION},
    )


def test_the_front_gets_an_internal_error(issue_asked: Json):
    response = answer_with_the_llm_down(issue_asked)

    assert response.status_code == 500
    assert response.json() == {"detail": "INTERNAL_ERROR"}


def test_the_conversation_stays_as_it_was(issue_asked: Json):
    answer_with_the_llm_down(issue_asked)

    assert get(issue_asked).json() == issue_asked


def test_the_same_answer_can_be_sent_again(issue_asked: Json):
    answer_with_the_llm_down(issue_asked)

    with fake_llm(reply.classify({"customer_message": DESCRIPTION}, SURELY_CANCEL)):
        response = answer(issue_asked, RequiredMessageId.ISSUE, DESCRIPTION)

    assert response.status_code == 200
    assert transcript(response.json()) == [
        *transcript(issue_asked),
        ("USER_ACTION_RESPONSE", RequiredMessageId.ISSUE, DESCRIPTION),
        ("ASSISTANT", OpeningCode.ASK_ISSUE_CHOICE.key),
        ISSUE_CHOICE_ASKED,
    ]
