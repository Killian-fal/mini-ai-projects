import pytest

from interactive_support_flow_api import InvalidAnswer
from interactive_support_flow_api.model.question import PhotoQuestion
from interactive_support_flow_api.model.question.photo import PhotoCode

QUESTION = PhotoQuestion()


def test_photo():
    photo = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ=="
    assert QUESTION.parse(photo) == photo


@pytest.mark.parametrize(
    "response",
    [
        pytest.param("Le bol est cassé", id="text"),
        pytest.param("/Users/me/bol.jpg", id="local path"),
        pytest.param("data:text/plain;base64,Ym9s", id="not an image"),
        pytest.param("data:image/jpeg;base64,", id="empty"),
        pytest.param("data:image/jpeg;base64,pas du base64", id="not base64"),
    ],
)
def test_not_a_photo(response: str):
    with pytest.raises(InvalidAnswer) as raised:
        QUESTION.parse(response)
    assert raised.value.error_code is PhotoCode.NOT_A_PHOTO


@pytest.mark.parametrize(
    "response",
    ["https://example.com/bol.jpg", "http://169.254.169.254/latest/meta-data"],
)
def test_url_not_accepted(response: str):
    with pytest.raises(InvalidAnswer) as raised:
        QUESTION.parse(response)
    assert raised.value.error_code is PhotoCode.URL_NOT_ACCEPTED
