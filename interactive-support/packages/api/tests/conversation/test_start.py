import pytest

from interactive_support_core.opening.code import OpeningCode

from .conftest import ISSUE_CHOICE_ASKED, TOO_LATE_TO_CANCEL, client, start, transcript


def test_the_first_message_opens_the_conversation():
    opened = start(TOO_LATE_TO_CANCEL)

    assert opened["language"] == "FR"
    assert transcript(opened) == [
        ("USER", TOO_LATE_TO_CANCEL),
        ("ASSISTANT", OpeningCode.ASK_ISSUE_CHOICE.key),
        ISSUE_CHOICE_ASKED,
    ]


@pytest.mark.parametrize(
    "message", ["", "a" * 2001], ids=["empty", "over_2000_characters"]
)
def test_a_first_message_empty_or_too_long_is_rejected(message: str):
    response = client.post("/conversations", json={"message": message})

    assert response.status_code == 422
