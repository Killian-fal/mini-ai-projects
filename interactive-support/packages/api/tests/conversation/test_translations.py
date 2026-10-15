from interactive_support_core.opening.code import IssueChoice
from interactive_support_core.opening.required_message_id import RequiredMessageId
from interactive_support_flow_cancel.address import AddressField

from .conftest import Json, answer, last


def test_a_code_comes_with_its_text(ended: Json):
    assert last(ended, "END")["text"] == "Merci, bonne journée !"


def test_each_choice_comes_with_its_label(issue_choice_asked: Json):
    # the front shows the labels and sends back a key
    assert last(issue_choice_asked, "ASSISTANT_ACTION")["action"]["choices"] == [
        {"key": IssueChoice.CANCEL.key, "label": "Annuler ma commande"},
        {"key": IssueChoice.OTHER.key, "label": "Autre chose"},
    ]


def test_each_form_field_comes_with_its_label(address_form_asked: Json):
    # pre-filled with what the LLM read, empty when it found nothing
    assert last(address_form_asked, "ASSISTANT_ACTION")["action"] == {
        "type": "FORM",
        "fields": [
            {
                "key": AddressField.STREET.key,
                "label": "Numéro et rue",
                "value": "5 rue Mercière",
            },
            {"key": AddressField.POSTAL_CODE.key, "label": "Code postal", "value": ""},
            {"key": AddressField.CITY.key, "label": "Ville", "value": "Lyon"},
        ],
    }


def test_a_chosen_option_comes_with_its_label(ended: Json):
    assert last(ended, "USER_ACTION_RESPONSE")["label"] == "Annuler ma commande"


def test_a_free_text_has_no_label(issue_choice_asked: Json):
    response = answer(issue_choice_asked, RequiredMessageId.ISSUE_CHOICE, "Annuler")

    assert last(response.json(), "USER_ACTION_RESPONSE")["label"] is None


def test_a_photo_has_no_label(report_to_confirm: Json):
    assert last(report_to_confirm, "USER_ACTION_RESPONSE")["label"] is None
