import pytest

from interactive_support_flow_cancel import geo


# answered before the API call: otherwise the fake API would fail with UNEXPECTED_GEOCODING
@pytest.mark.parametrize(
    "address",
    [
        pytest.param("5", id="too short"),
        pytest.param("5 rue Mercière" * 15, id="too long"),
        pytest.param("(5) rue Mercière, 69002 Lyon", id="starts with a sign"),
    ],
)
def test_an_address_the_api_refuses_is_not_searched(address: str):
    assert geo.geocode(address) is None
