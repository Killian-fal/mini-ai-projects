import zlib
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Self

from store.connection import Document
from store.detections.schema import Detection
from store.runs.schema import RunKey

type SortField = Literal["score", "analysed_at", "html_bytes"]
type Order = Literal["asc", "desc"]


@dataclass(frozen=True, slots=True)
class Page:
    """Raw page, as the analysis reads it."""

    id: str
    url: str
    bucket: str
    headers: str
    html: str

    @classmethod
    def from_doc(cls, doc: Document) -> Self:
        return cls(
            id=str(doc["_id"]),
            url=doc["url"],
            bucket=doc["bucket"],
            headers=doc.get("headers", ""),
            html=zlib.decompress(doc["html"]).decode(),
        )


@dataclass(frozen=True, slots=True)
class PageRow:
    """A list row: the page and the state of its last detection."""

    id: str
    url: str
    host: str | None
    bucket: str
    crawl: str
    html_bytes: int
    fetched_at: datetime
    flagged: bool
    channels: list[str]
    score: float | None = None
    threshold: float | None = None
    error: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency_ms: int | None = None
    analysed_at: datetime | None = None

    @classmethod
    def from_doc(cls, doc: Document) -> Self:
        return cls(**doc)  # shaped by pipeline.ROW


@dataclass(frozen=True, slots=True)
class PageList:
    items: list[PageRow]
    total: int
    flagged_total: int


@dataclass(frozen=True, slots=True)
class PageDetail:
    id: str
    url: str
    host: str | None
    bucket: str
    crawl: str
    headers: str
    html_bytes: int
    fetched_at: datetime
    detections: list[Detection]

    @classmethod
    def from_doc(cls, doc: Document) -> Self:
        return cls(
            id=str(doc["_id"]),
            url=doc["url"],
            host=doc["host"],
            bucket=doc["bucket"],
            crawl=doc["crawl"],
            headers=doc["headers"],
            html_bytes=doc["html_bytes"],
            fetched_at=doc["fetched_at"],
            detections=[Detection.from_doc(d) for d in doc["detections"]],
        )


@dataclass(frozen=True, slots=True)
class PageFilters:
    q: str | None = None
    buckets: list[str] | None = None
    crawl: str | None = None
    run: RunKey | None = None
    flagged_only: bool = False
    with_error: bool = False
    min_score: float | None = None
