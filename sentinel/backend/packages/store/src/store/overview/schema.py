from dataclasses import dataclass

from store.pages.schema import PageRow


@dataclass(frozen=True, slots=True)
class BucketCount:
    bucket: str
    count: int
    flagged: int


@dataclass(frozen=True, slots=True)
class Overview:
    stored: int
    analysed: int
    flagged: int
    runs: int
    input_tokens: int
    histogram: list[int]
    threshold: float | None
    buckets: list[BucketCount]
    latest_flagged: list[PageRow]
