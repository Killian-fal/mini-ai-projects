import zlib
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlsplit

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from store.connection import collections
from store.error import guarded

KNOWN_CHUNK = 10_000  # a single $in over a whole index part nears the 16 MB BSON limit


def known_urls(urls: list[str]) -> set[str]:
    found: set[str] = set()
    with guarded():
        for i in range(0, len(urls), KNOWN_CHUNK):
            chunk = urls[i : i + KNOWN_CHUNK]
            found |= {d["url"] for d in collections().pages.find({"url": {"$in": chunk}}, {"url": 1})}
    return found


def save_page(  # noqa: PLR0913
    url: str, bucket: str, crawl: str, headers: str, html: str, *, tranco: str = "unranked"
) -> str | None:
    """Id of the created page, None if the URL is already stored."""
    body = html.encode()
    page_id = ObjectId()
    doc: dict[str, Any] = {
        "_id": page_id,
        "url": url,
        "host": urlsplit(url).hostname,
        "bucket": bucket,
        "tranco": tranco,
        "crawl": crawl,
        "headers": headers,
        "html_bytes": len(body),
        "fetched_at": datetime.now(UTC),
        "detections": [],
    }
    with guarded():
        # HTML first: a page without HTML breaks the analysis, an orphan HTML document does not
        collections().html.insert_one({"_id": page_id, "html": zlib.compress(body)})
        try:
            collections().pages.insert_one(doc)
        except DuplicateKeyError:
            collections().html.delete_one({"_id": page_id})
            return None
    return str(page_id)
