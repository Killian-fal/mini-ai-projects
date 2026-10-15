import pytest

from interactive_support_core.opening.detection import extract_order_number


@pytest.mark.parametrize(
    "text, expected",
    [
        ("cma_001", "#CMA_001"),
        ("#CMA_001", "#CMA_001"),
        ("Ma commande Cma_12ab n'est pas arrivée", "#CMA_12AB"),
        ("Ma commande n'est pas arrivée", None),
    ],
)
def test_extract_order_number(text: str, expected: str | None):
    assert extract_order_number(text) == expected
