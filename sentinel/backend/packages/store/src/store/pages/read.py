import re
import zlib
from collections.abc import Iterator
from itertools import islice
from typing import Any

from bson import ObjectId

from store.connection import UNDETECTED, Document, collections
from store.error import guarded
from store.pages.pipeline import LAST, ROW, count
from store.pages.schema import Order, Page, PageDetail, PageFilters, PageList, PageRow, SortField
from store.runs.schema import RunKey

HTML_CHUNK = 100  # pages joined to their HTML in one $in
SORT_FIELDS: dict[SortField, str] = {
    "score": "last.score",
    "analysed_at": "last.at",
    "html_bytes": "html_bytes",
}


def crawls() -> list[str]:
    with guarded():
        return sorted(collections().pages.distinct("crawl"))


def iter_pages(limit: int | None = None, *, undetected: bool = False) -> Iterator[Page]:
    # the planner never picks on its own a partial index whose key is absent from the query
    query: dict[str, Any] = {"detections": []} if undetected else {}
    hint = UNDETECTED if undetected else None
    fields = {"url": 1, "bucket": 1, "headers": 1}
    with guarded():
        cursor = collections().pages.find(query, fields, limit=limit or 0, hint=hint)
        while batch := list(islice(cursor, HTML_CHUNK)):
            bodies = {d["_id"]: d["html"] for d in _bodies([d["_id"] for d in batch])}
            # a page without HTML comes from an interrupted insert
            yield from (Page.from_doc(d | {"html": bodies[d["_id"]]}) for d in batch if d["_id"] in bodies)


def list_pages(filters: PageFilters, sort: SortField, order: Order, page: int, size: int) -> PageList:
    # ponytail: sort after $addFields, so without an index; store the last score if listing gets slow
    direction = 1 if order == "asc" else -1
    facet = {
        "items": [
            {"$sort": {SORT_FIELDS[sort]: direction, "_id": direction}},
            {"$skip": (page - 1) * size},
            {"$limit": size},
            ROW,
        ],
        "total": [{"$count": "n"}],
        "flagged": [{"$match": {"last.flagged": True}}, {"$count": "n"}],
    }
    pipeline: list[dict[str, Any]] = [LAST, {"$match": _list_match(filters)}, {"$facet": facet}]
    with guarded():
        result = next(collections().pages.aggregate(pipeline))
    return PageList(
        items=[PageRow.from_doc(r) for r in result["items"]],
        total=count(result["total"]),
        flagged_total=count(result["flagged"]),
    )


def get_page(page_id: str) -> PageDetail | None:
    if not ObjectId.is_valid(page_id):
        return None
    with guarded():
        doc = collections().pages.find_one({"_id": ObjectId(page_id)})
    return None if doc is None else PageDetail.from_doc(doc)


def page_request(page_id: str) -> str | None:
    """JSON body sent to Jev for the last detection."""
    if not ObjectId.is_valid(page_id):
        return None
    with guarded():
        doc = collections().pages.find_one({"_id": ObjectId(page_id)}, {"detections": {"$slice": -1}})
    last = doc["detections"][0] if doc and doc["detections"] else {}
    raw = last.get("request")
    return None if raw is None else zlib.decompress(raw).decode()


def page_html(page_id: str) -> str | None:
    if not ObjectId.is_valid(page_id):
        return None
    with guarded():
        doc = collections().html.find_one({"_id": ObjectId(page_id)})
    return None if doc is None else zlib.decompress(doc["html"]).decode()


def _bodies(page_ids: list[ObjectId]) -> Iterator[Document]:
    return collections().html.find({"_id": {"$in": page_ids}})


def _run_match(run: RunKey) -> dict[str, Any]:
    return {
        "last.model": run.model,
        "last.threshold": run.threshold,
        "$expr": {"$eq": [{"$dateTrunc": {"date": "$last.at", "unit": "minute"}}, run.minute]},
    }


def _list_match(filters: PageFilters) -> dict[str, Any]:
    match: dict[str, Any] = {}
    if filters.q:
        match["url"] = {"$regex": re.escape(filters.q), "$options": "i"}
    if filters.buckets:
        match["bucket"] = {"$in": filters.buckets}
    if filters.crawl:
        match["crawl"] = filters.crawl
    if filters.flagged_only:
        match["last.flagged"] = True
    if filters.with_error:
        match["last.error"] = {"$type": "string"}
    if filters.min_score is not None:
        match["last.score"] = {"$gte": filters.min_score}
    if filters.run:
        match |= _run_match(filters.run)
    return match
