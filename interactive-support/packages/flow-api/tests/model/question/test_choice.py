from enum import auto

import pytest

from interactive_support_flow_api import InvalidAnswer
from interactive_support_flow_api.model.message import TextCode
from interactive_support_flow_api.model.question import ChoiceQuestion
from interactive_support_flow_api.model.question.choice import ChoiceCode


class Color(TextCode):
    RED = auto()
    GREEN = auto()
    BLUE = auto()


COLOR = ChoiceQuestion(options=[Color.RED, Color.GREEN])


def test_choice_is_read_from_its_key():
    assert COLOR.parse("Color.GREEN") is Color.GREEN


@pytest.mark.parametrize(
    "response",
    [
        pytest.param("GREEN", id="name without its owner"),
        pytest.param("color.green", id="other case"),
        pytest.param("Color.BLUE", id="not proposed"),
        pytest.param("", id="empty"),
    ],
)
def test_unknown_choice(response: str):
    with pytest.raises(InvalidAnswer) as raised:
        COLOR.parse(response)
    assert raised.value.error_code is ChoiceCode.UNKNOWN_CHOICE
