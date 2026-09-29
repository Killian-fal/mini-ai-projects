# Aggregation stages shared by the page list and the overview.

LAST = {"$addFields": {"last": {"$arrayElemAt": ["$detections", -1]}}}
# same names as the PageRow fields
ROW = {
    "$project": {
        "_id": 0,
        "id": {"$toString": "$_id"},
        "url": 1,
        "host": 1,
        "bucket": 1,
        "crawl": 1,
        "html_bytes": 1,
        "fetched_at": 1,
        "score": "$last.score",
        "threshold": "$last.threshold",
        "flagged": {"$ifNull": ["$last.flagged", False]},
        "error": "$last.error",
        "input_tokens": "$last.usage.input_tokens",
        "output_tokens": "$last.usage.output_tokens",
        "latency_ms": "$last.latency_ms",
        "analysed_at": "$last.at",
        "channels": {"$ifNull": ["$last.channels", []]},
    }
}


def count(facet: list[dict[str, int]]) -> int:
    """Value of a facet ending with {"$count": "n"}, 0 when empty."""
    return facet[0]["n"] if facet else 0
