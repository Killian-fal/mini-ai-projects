import pytest
from store import PageFilters, StoreError, list_pages


@pytest.mark.usefixtures("db")
def test_a_mongo_failure_leaves_the_package_as_a_store_error() -> None:
    with pytest.raises(StoreError, match="skip"):
        list_pages(PageFilters(), "score", "desc", 0, 10)  # Mongo rejects a negative $skip
