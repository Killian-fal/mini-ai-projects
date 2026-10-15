# pyright: reportPrivateUsage=false
# the geocoding API CANCEL calls is replaced where it is called
import json
from importlib import import_module

import pytest

from interactive_support_core.opening.code import IssueChoice, OpeningCode
from interactive_support_core.opening.required_message_id import RequiredMessageId
from interactive_support_flow_api.model.question.choice import ChoiceCode
from interactive_support_flow_api.model.question import Location
from interactive_support_flow_cancel import CANCEL_FLOW
from interactive_support_flow_cancel.address import AddressField
from interactive_support_flow_cancel.code import CancelCode
from interactive_support_flow_cancel import geo
from interactive_support_flow_cancel.flow import CancelStep
from interactive_support_flow_damaged import DAMAGED_FLOW
from interactive_support_flow_damaged.code import DamagedCode
from interactive_support_flow_damaged.flow import DamagedStep

from .conftest import (
    ISSUE_CHOICE_ASKED,
    PHOTO,
    PHOTO_ASKED,
    REPORT,
    UNKNOWN,
    Json,
    answer,
    get,
    last,
    send_photo,
    transcript,
)


def test_an_answer_plays_its_turn(issue_choice_asked: Json):
    response = answer(
        issue_choice_asked, RequiredMessageId.ISSUE_CHOICE, IssueChoice.CANCEL.key
    )

    assert response.status_code == 200
    conversation = response.json()
    assert conversation["id"] == issue_choice_asked["id"]
    assert transcript(conversation) == [
        *transcript(issue_choice_asked),
        (
            "USER_ACTION_RESPONSE",
            RequiredMessageId.ISSUE_CHOICE,
            IssueChoice.CANCEL.key,
        ),
        ("ASSISTANT", OpeningCode.VALID_ISSUE.key),
        ("ASSISTANT", CancelCode.TOO_LATE_TO_CANCEL.key),
        ("END", OpeningCode.COMPLETE_CONVERSATION.key),
    ]


def test_an_invalid_answer_asks_the_same_question_again(issue_choice_asked: Json):
    response = answer(issue_choice_asked, RequiredMessageId.ISSUE_CHOICE, "Annuler")

    assert response.status_code == 200
    assert transcript(response.json()) == [
        *transcript(issue_choice_asked),
        ("USER_ACTION_RESPONSE", RequiredMessageId.ISSUE_CHOICE, "Annuler"),
        ("ASSISTANT", ChoiceCode.UNKNOWN_CHOICE.key),
        ISSUE_CHOICE_ASKED,
    ]


def test_a_photo_asks_to_confirm_the_report_written_from_it(photo_asked: Json):
    response = send_photo(photo_asked)

    assert response.status_code == 200
    confirmation = response.json()
    assert transcript(confirmation) == [
        *transcript(photo_asked),
        ("USER_ACTION_RESPONSE", PHOTO_ASKED, PHOTO),
        ("ASSISTANT", DamagedCode.ASK_REPORT_CONFIRMATION.key),
        (
            "ASSISTANT_ACTION",
            DAMAGED_FLOW.action_id(DamagedStep.REPORT_CONFIRMATION),
            "YES_NO",
        ),
    ]
    # the report the LLM wrote, kept in the context's extensions
    assert last(confirmation, "ASSISTANT_ACTION")["action"] == {
        "type": "YES_NO",
        "value": REPORT,
        "location": None,
    }


def test_an_address_found_is_confirmed_on_a_map(
    address_form_asked: Json, monkeypatch: pytest.MonkeyPatch
):
    found = geo.Address(
        label="5 Rue Mercière 69002 Lyon",
        location=Location(latitude=45.764324, longitude=4.832535),
    )
    monkeypatch.setattr(
        import_module("interactive_support_flow_cancel.geo.geocode"),
        "_search",
        {"5 rue Mercière, 69002 Lyon": found}.get,
    )
    response = answer(
        address_form_asked,
        CANCEL_FLOW.action_id(CancelStep.ADDRESS_DETAILS),
        json.dumps(
            {
                AddressField.STREET.key: "5 rue Mercière",
                AddressField.POSTAL_CODE.key: "69002",
                AddressField.CITY.key: "Lyon",
            }
        ),
    )

    assert response.status_code == 200
    assert last(response.json(), "ASSISTANT_ACTION")["action"] == {
        "type": "YES_NO",
        "value": "5 Rue Mercière 69002 Lyon",
        "location": {"latitude": 45.764324, "longitude": 4.832535},
    }


def test_an_answer_once_its_turn_is_over_is_a_conflict(ended: Json):
    # a stale tab, a replay: the question isn't pending anymore
    response = answer(ended, RequiredMessageId.ISSUE_CHOICE, IssueChoice.CANCEL.key)

    assert response.status_code == 409
    assert response.json() == {"detail": "ACTION_NOT_FOUND:OPENING.ISSUE_CHOICE"}
    assert get(ended).json() == ended


def test_an_answer_over_10_000_000_characters_is_rejected(issue_choice_asked: Json):
    response = answer(
        issue_choice_asked, RequiredMessageId.ISSUE_CHOICE, "a" * 10_000_001
    )

    assert response.status_code == 422
    assert get(issue_choice_asked).json() == issue_choice_asked


def test_an_unknown_conversation_is_not_found():
    response = answer(UNKNOWN, RequiredMessageId.ISSUE, "Bonjour")

    assert response.status_code == 404
    assert response.json() == {"detail": "CONVERSATION_NOT_FOUND"}
