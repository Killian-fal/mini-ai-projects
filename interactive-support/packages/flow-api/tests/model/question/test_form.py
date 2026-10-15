from enum import auto

import pytest

from interactive_support_flow_api import InvalidAnswer
from interactive_support_flow_api.model.message import TextCode
from interactive_support_flow_api.model.question import ActionForm, FormQuestion
from interactive_support_flow_api.model.question.form import FormCode


class Address(TextCode):
    STREET = auto()
    CITY = auto()


ADDRESS = FormQuestion(
    fields=[Address.STREET, Address.CITY], values={Address.CITY: "Lyon"}
)


def test_the_form_is_shown_pre_filled_in_order():
    assert ADDRESS.action() == ActionForm(
        fields={"Address.STREET": "", "Address.CITY": "Lyon"}
    )


def test_every_field_is_read_from_its_key():
    response = '{"Address.CITY": " Lyon ", "Address.STREET": "5 rue Mercière", "Other.KEY": "ignored"}'

    assert ADDRESS.parse(response) == {
        Address.STREET: "5 rue Mercière",
        Address.CITY: "Lyon",
    }


@pytest.mark.parametrize(
    "response",
    [
        pytest.param("5 rue Mercière, Lyon", id="text"),
        pytest.param('["5 rue Mercière", "Lyon"]', id="not an object"),
        pytest.param('{"Address.STREET": 5, "Address.CITY": "Lyon"}', id="not a text"),
        pytest.param("", id="empty"),
    ],
)
def test_not_a_form(response: str):
    with pytest.raises(InvalidAnswer) as raised:
        ADDRESS.parse(response)
    assert raised.value.error_code is FormCode.NOT_A_FORM


@pytest.mark.parametrize(
    "response",
    [
        pytest.param('{"Address.STREET": "5 rue Mercière"}', id="missing"),
        pytest.param(
            '{"Address.STREET": "5 rue Mercière", "Address.CITY": "  "}', id="blank"
        ),
        pytest.param(
            '{"STREET": "5 rue Mercière", "CITY": "Lyon"}', id="name without its owner"
        ),
    ],
)
def test_missing_field(response: str):
    with pytest.raises(InvalidAnswer) as raised:
        ADDRESS.parse(response)
    assert raised.value.error_code is FormCode.MISSING_FIELD
