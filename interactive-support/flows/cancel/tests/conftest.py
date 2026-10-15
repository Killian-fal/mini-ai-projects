# pyright: reportPrivateUsage=false
# the in-memory orders have no reset: the test swaps their store. The geocoding API is replaced where it is called
from importlib import import_module

import pytest

from interactive_support_domain_order import crud
from interactive_support_flow_cancel import geo


@pytest.fixture(autouse=True)
def _isolated_orders(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    The orders live in memory: each test starts from the seeds, whatever the previous one changed.
    #CMA_001 not prepared (home), #CMA_002 in preparation (relay point), #CMA_003 shipped, #CMA_004 delivered.
    """
    monkeypatch.setattr(crud, "_ORDERS", crud._ORDERS.copy())


@pytest.fixture(autouse=True)
def geocoded(monkeypatch: pytest.MonkeyPatch) -> dict[str, geo.Address | None]:
    """
    The geocoding API, faked: a test fills what it answers for each address the flow searches, None when the address
    doesn't exist. Searching any other address fails the test.
    """
    answers: dict[str, geo.Address | None] = {}

    def search(address: str) -> geo.Address | None:
        if address not in answers:
            raise AssertionError(f"UNEXPECTED_GEOCODING:{address}")
        return answers[address]

    # import_module: `geo.geocode` is the function the package exports, not the module
    monkeypatch.setattr(
        import_module("interactive_support_flow_cancel.geo.geocode"), "_search", search
    )
    return answers
