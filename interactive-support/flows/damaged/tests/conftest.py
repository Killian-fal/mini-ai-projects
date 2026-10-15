# pyright: reportPrivateUsage=false
# the in-memory orders have no reset: the test swaps their store
import pytest

from interactive_support_domain_order import crud


@pytest.fixture(autouse=True)
def _isolated_orders(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    The orders live in memory: each test starts from the seeds, whatever the previous one changed.
    #CMA_001 not prepared (home), #CMA_002 in preparation (relay point), #CMA_003 shipped, #CMA_004 delivered.
    """
    monkeypatch.setattr(crud, "_ORDERS", crud._ORDERS.copy())
