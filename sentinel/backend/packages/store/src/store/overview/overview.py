from typing import Any

from store.connection import collections
from store.error import guarded
from store.overview.schema import BucketCount, Overview
from store.pages.pipeline import LAST, ROW, count
from store.pages.schema import PageRow
from store.runs.runs import RUN_KEY

HISTOGRAM_BINS = 20
FACET = {
    "counts": [
        {
            "$group": {
                "_id": None,
                "stored": {"$sum": 1},
                "analysed": {"$sum": {"$cond": [{"$gt": [{"$size": "$detections"}, 0]}, 1, 0]}},
                "flagged": {"$sum": {"$cond": ["$last.flagged", 1, 0]}},
                "input_tokens": {"$sum": {"$sum": "$detections.usage.input_tokens"}},
            }
        }
    ],
    "histogram": [
        {"$match": {"last.score": {"$type": "number"}}},
        {
            "$group": {
                "_id": {
                    "$min": [HISTOGRAM_BINS - 1, {"$floor": {"$multiply": ["$last.score", HISTOGRAM_BINS]}}]
                },
                "count": {"$sum": 1},
            }
        },
    ],
    "runs": [
        {"$unwind": "$detections"},
        {"$group": {"_id": RUN_KEY}},
        {"$count": "n"},
    ],
    "buckets": [
        {
            "$group": {
                "_id": "$bucket",
                "count": {"$sum": 1},
                "flagged": {"$sum": {"$cond": ["$last.flagged", 1, 0]}},
            }
        },
        {"$sort": {"_id": 1}},
    ],
    "threshold": [
        {"$match": {"last.at": {"$exists": True}}},
        {"$sort": {"last.at": -1, "_id": -1}},
        {"$limit": 1},
        {"$project": {"_id": 0, "threshold": "$last.threshold"}},
    ],
    "latest_flagged": [
        {"$match": {"last.flagged": True}},
        {"$sort": {"last.at": -1, "_id": -1}},
        {"$limit": 10},
        ROW,
    ],
}


def overview(crawl: str | None) -> Overview:
    pipeline: list[dict[str, Any]] = [{"$match": {"crawl": crawl}}] if crawl else []
    with guarded():
        result = next(collections().pages.aggregate([*pipeline, LAST, {"$facet": FACET}]))
    counts = result["counts"][0] if result["counts"] else {}
    histogram = [0] * HISTOGRAM_BINS
    for h in result["histogram"]:
        histogram[int(h["_id"])] = h["count"]
    return Overview(
        stored=counts.get("stored", 0),
        analysed=counts.get("analysed", 0),
        flagged=counts.get("flagged", 0),
        runs=count(result["runs"]),
        input_tokens=counts.get("input_tokens", 0),
        histogram=histogram,
        threshold=result["threshold"][0]["threshold"] if result["threshold"] else None,
        buckets=[
            BucketCount(bucket=b["_id"], count=b["count"], flagged=b["flagged"]) for b in result["buckets"]
        ],
        latest_flagged=[PageRow.from_doc(r) for r in result["latest_flagged"]],
    )
