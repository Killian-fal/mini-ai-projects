import hashlib
from datetime import UTC, datetime

from pymongo import UpdateOne

from store.connection import collections
from store.error import guarded


def bleached(blocks: list[str]) -> set[str]:
    by_id = {_id(b): b for b in blocks}
    with guarded():
        found = collections().blocks.find({"_id": {"$in": list(by_id)}}, {"_id": 1})
        return {by_id[d["_id"]] for d in found}


def bleach(blocks: list[str]) -> None:
    now = datetime.now(UTC)
    writes = [
        UpdateOne({"_id": i}, {"$setOnInsert": {"at": now}}, upsert=True) for i in {_id(b) for b in blocks}
    ]
    if writes:
        with guarded():
            collections().blocks.bulk_write(writes, ordered=False)


def _id(block: str) -> str:
    return hashlib.sha1(block.encode(), usedforsecurity=False).hexdigest()
