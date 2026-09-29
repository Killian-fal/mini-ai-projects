import os
from dataclasses import dataclass
from functools import cache
from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from store.error import StoreError

type Document = dict[str, Any]

DATABASE = "job"
UNDETECTED = "undetected"


@dataclass(frozen=True, slots=True)
class Collections:
    pages: Collection[Document]
    html: Collection[Document]
    blocks: Collection[Document]


@cache
def collections() -> Collections:
    url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    client: MongoClient[Document] = MongoClient(url, tz_aware=True, serverSelectionTimeoutMS=3000)
    db = client[DATABASE]
    pages = db["pages"]
    try:
        pages.create_index("url", unique=True)
        pages.create_index("bucket")
        # never-analysed pages: the index iter_pages(undetected=True) hints by name
        pages.create_index("fetched_at", name=UNDETECTED, partialFilterExpression={"detections": {"$eq": []}})
    except PyMongoError as e:
        client.close()
        raise StoreError(f"mongo injoignable sur {url}: {e}") from e
    # html and blocks: _id is the page id and the block sha1, so their only index is the implicit one
    return Collections(pages=pages, html=db["html"], blocks=db["blocks"])
