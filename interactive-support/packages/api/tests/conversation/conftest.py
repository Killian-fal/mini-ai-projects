from typing import Any

import httpx2
import pytest
from fastapi.testclient import TestClient

from interactive_support_api.app import app
from interactive_support_core.opening.code import IssueChoice
from interactive_support_core.opening.detection.issue import (
    ISSUE_QUESTION,
    IssueDetection,
)
from interactive_support_core.opening.detection.language import (
    LANGUAGE_QUESTION,
    LanguageDetection,
)
from interactive_support_core.opening.required_message_id import RequiredMessageId
from interactive_support_flow_api.model.context import Language
from interactive_support_flow_api.tools import llm
from interactive_support_flow_cancel import CANCEL_FLOW
from interactive_support_flow_cancel.address import AddressInput, ExtractedAddress
from interactive_support_flow_cancel.flow import CancelProposal, CancelStep
from interactive_support_flow_damaged import DAMAGED_FLOW
from interactive_support_flow_damaged.flow import DamagedStep
from interactive_support_flow_damaged.report import ReportInput, WrittenReport
from interactive_support_flow_test import fake_llm, reply
from interactive_support_flow_test.reply import Answer

type Json = dict[str, Any]

client = TestClient(app)

FRENCH = reply.choose(LANGUAGE_QUESTION, LanguageDetection.FR)
SURELY_CANCEL = reply.choose(ISSUE_QUESTION, IssueDetection["CANCEL"])
ISSUE_CHOICE_ASKED = (
    "ASSISTANT_ACTION",
    RequiredMessageId.ISSUE_CHOICE,
    "UNIQUE_CHOICE",
    IssueChoice.CANCEL.key,
    IssueChoice.OTHER.key,
)
# #CMA_003 is shipped: CANCEL refuses and ends, the order doesn't change
TOO_LATE_TO_CANCEL = "Bonjour, je veux annuler ma commande cma_003"
PHOTO_ASKED = DAMAGED_FLOW.action_id(DamagedStep.PHOTO)
PHOTO = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ=="
REPORT = "Le carton est écrasé"
NEW_ADDRESS = "Je déménage au 5 rue Mercière à Lyon"
UNKNOWN: Json = {"id": "unknown"}


def start(message: str, issue: Answer = SURELY_CANCEL) -> Json:
    with fake_llm(reply.classify({"customer_message": message}, FRENCH, issue)):
        response = client.post("/conversations", json={"message": message})
    assert response.status_code == 201
    return response.json()


def answer(conversation: Json, action_id: str, response: str) -> httpx2.Response:
    return client.post(
        f"/conversations/{conversation['id']}/answers",
        json={"action_id": action_id, "response": response},
    )


def get(conversation: Json) -> httpx2.Response:
    return client.get(f"/conversations/{conversation['id']}")


def send_photo(asked: Json) -> httpx2.Response:
    report_input = ReportInput(
        photo=llm.Image(PHOTO),
        refused_report=None,
        correction=None,
        language=Language.FR,
    )
    with fake_llm(
        reply.generate(given=report_input, output=WrittenReport(report=REPORT))
    ):
        return answer(asked, PHOTO_ASKED, PHOTO)


def last(conversation: Json, role: str) -> Json:
    return next(
        message
        for message in reversed(conversation["messages"])
        if message["role"] == role
    )


def transcript(conversation: Json) -> list[tuple[str, ...]]:
    """
    Each message by its role and what identifies it: a text, a code, an answer, the question with its keys.
    The translations aside: test_translations.py checks them.
    """
    result: list[tuple[str, ...]] = []
    for message in conversation["messages"]:
        match message["role"]:
            case "USER" | "ASSISTANT_GEN":
                result.append((message["role"], message["text"]))
            case "ASSISTANT" | "END":
                result.append((message["role"], message["code"]))
            case "ASSISTANT_ACTION":
                action = message["action"]
                keys = [choice["key"] for choice in action.get("choices", [])]
                result.append(
                    (message["role"], message["action_id"], action["type"], *keys)
                )
            case "USER_ACTION_RESPONSE":
                result.append(
                    (message["role"], message["action_id"], message["response"])
                )
            case _:
                raise AssertionError(f"UNEXPECTED_MESSAGE:{message}")
    return result


@pytest.fixture
def issue_choice_asked() -> Json:
    return start(TOO_LATE_TO_CANCEL)


@pytest.fixture
def ended(issue_choice_asked: Json) -> Json:
    response = answer(
        issue_choice_asked, RequiredMessageId.ISSUE_CHOICE, IssueChoice.CANCEL.key
    )
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def issue_asked() -> Json:
    return start("Bonjour", reply.choose(ISSUE_QUESTION, IssueDetection["OTHER"]))


@pytest.fixture
def photo_asked() -> Json:
    # #CMA_004 is delivered: DAMAGED asks a photo
    opened = start(
        "Ma commande cma_004 est arrivée cassée",
        reply.choose(ISSUE_QUESTION, IssueDetection["DAMAGED"]),
    )
    response = answer(opened, RequiredMessageId.ISSUE_CHOICE, IssueChoice.DAMAGED.key)
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def report_to_confirm(photo_asked: Json) -> Json:
    # stops before "true": sending the report changes the order
    response = send_photo(photo_asked)
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def address_form_asked() -> Json:
    # #CMA_001 is not prepared: CANCEL offers to change the address. Stops at the form, before the order changes
    opened = start("Je veux annuler ma commande cma_001")
    answer(opened, RequiredMessageId.ISSUE_CHOICE, IssueChoice.CANCEL.key)
    answer(
        opened,
        CANCEL_FLOW.action_id(CancelStep.PROPOSAL_NOT_PREPARED),
        CancelProposal.CHANGE_ADDRESS.key,
    )
    read = ExtractedAddress(street="5 rue Mercière", postal_code=None, city="Lyon")
    with fake_llm(reply.generate(given=AddressInput(message=NEW_ADDRESS), output=read)):
        response = answer(
            opened, CANCEL_FLOW.action_id(CancelStep.NEW_ADDRESS), NEW_ADDRESS
        )
    assert response.status_code == 200
    return response.json()
