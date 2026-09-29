from datetime import UTC, datetime, time, timedelta
from typing import Any

from store.connection import collections
from store.error import guarded
from store.runs.schema import DayCount, Run, RunKey

_FLAGGED = {"$sum": {"$cond": ["$detections.flagged", 1, 0]}}
_IN = {"$ifNull": ["$detections.usage.input_tokens", 0]}
_OUT = {"$ifNull": ["$detections.usage.output_tokens", 0]}
# also counts the runs in the overview
RUN_KEY = {
    "minute": {"$dateTrunc": {"date": "$detections.at", "unit": "minute"}},
    "model": "$detections.model",
    "threshold": "$detections.threshold",
}


def runs() -> list[Run]:
    pipeline: list[dict[str, Any]] = [
        {"$unwind": "$detections"},
        {
            "$group": {
                "_id": RUN_KEY,
                "analysed": {"$sum": 1},
                "flagged": _FLAGGED,
                "errors": {"$sum": {"$cond": [{"$eq": [{"$type": "$detections.error"}, "string"]}, 1, 0]}},
                "input_tokens": {"$sum": _IN},
                "output_tokens": {"$sum": _OUT},
                "duration_ms": {"$sum": {"$ifNull": ["$detections.latency_ms", 0]}},
                "median_latency_ms": {
                    "$median": {"input": "$detections.latency_ms", "method": "approximate"}
                },
            }
        },
        {"$sort": {"_id.minute": -1, "_id.model": 1, "_id.threshold": 1}},
    ]
    with guarded():
        return [
            Run(key=RunKey(**r.pop("_id")), **r)  # $group keys = Run fields
            for r in collections().pages.aggregate(pipeline)
        ]


def daily(days: int) -> list[DayCount]:
    """The last `days` UTC days, today included, empty days as zeros."""
    first = datetime.now(UTC).date() - timedelta(days=days - 1)
    pipeline: list[dict[str, Any]] = [
        {"$unwind": "$detections"},
        {"$match": {"detections.at": {"$gte": datetime.combine(first, time.min, UTC)}}},
        {
            "$group": {
                "_id": {"$dateToString": {"date": "$detections.at", "format": "%Y-%m-%d"}},
                "analysed": {"$sum": 1},
                "flagged": _FLAGGED,
            }
        },
    ]
    with guarded():
        counts = {r["_id"]: (r["analysed"], r["flagged"]) for r in collections().pages.aggregate(pipeline)}
    dates = (first + timedelta(days=i) for i in range(days))
    return [DayCount(d, *counts.get(d.isoformat(), (0, 0))) for d in dates]
