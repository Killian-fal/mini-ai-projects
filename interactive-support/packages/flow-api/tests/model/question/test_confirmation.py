import pytest

from interactive_support_flow_api import InvalidAnswer
from interactive_support_flow_api.model.question import ConfirmationQuestion
from interactive_support_flow_api.model.question.confirmation import ConfirmationCode

QUESTION = ConfirmationQuestion(value="5 rue Mercière")


@pytest.mark.parametrize(
    "response, value",
    [
        ("true", True),
        ("false", False),
        ("Yes", True),
        ("no", False),
        ("1", True),
        ("0", False),
        ("on", True),
        ("off", False),
    ],
)
def test_confirmation(response: str, value: bool):
    assert QUESTION.parse(response) is value


@pytest.mark.parametrize("response", ["oui", "peut-être", ""])
def test_not_a_boolean(response: str):
    with pytest.raises(InvalidAnswer) as raised:
        QUESTION.parse(response)
    assert raised.value.error_code is ConfirmationCode.NOT_A_BOOLEAN
