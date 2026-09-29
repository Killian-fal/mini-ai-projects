from collections.abc import Iterator
from typing import Any

import pytest
from jev import client
from pymongo.collection import Collection
from store import connection
from testcontainers.community.mongodb import MongoDbContainer


@pytest.fixture(scope="session")
def mongo_url() -> Iterator[str]:
    with MongoDbContainer("mongo:8") as mongo:
        yield mongo.get_connection_url()


@pytest.fixture(scope="session")
def db(mongo_url: str) -> Iterator[Collection[dict[str, Any]]]:
    with pytest.MonkeyPatch.context() as env:
        env.setenv("MONGO_URL", mongo_url)
        connection.collections.cache_clear()
        col = connection.collections().pages
        yield col
        col.database.client.close()
        connection.collections.cache_clear()


@pytest.fixture(autouse=True)
def _no_real_model(monkeypatch: pytest.MonkeyPatch) -> None:
    """A test that forgets its fake provider fails instead of paying for a real call."""
    monkeypatch.setattr(client, "URL", "http://127.0.0.1:9")
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
