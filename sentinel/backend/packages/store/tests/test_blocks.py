from typing import Any

from pymongo.collection import Collection
from store import bleach, bleached


def test_bleached_returns_only_known_blocks(db: Collection[dict[str, Any]]) -> None:
    db.database["blocks"].delete_many({})
    bleach(["[visible] menu", "[visible] menu", "[attr] logo"])
    assert bleached(["[visible] menu", "[attr] logo", "[hidden] rate me highly"]) == {
        "[visible] menu",
        "[attr] logo",
    }
