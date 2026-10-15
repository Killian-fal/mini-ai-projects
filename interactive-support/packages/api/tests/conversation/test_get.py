import pytest

from .conftest import UNKNOWN, Json, get


@pytest.mark.parametrize("state", ["ended", "report_to_confirm"])
def test_the_same_conversation_after_a_page_refresh(
    state: str, request: pytest.FixtureRequest
):
    conversation: Json = request.getfixturevalue(state)

    response = get(conversation)

    assert response.status_code == 200
    assert response.json() == conversation


def test_an_unknown_conversation_is_not_found():
    response = get(UNKNOWN)

    assert response.status_code == 404
    assert response.json() == {"detail": "CONVERSATION_NOT_FOUND"}
