from datetime import date, datetime
from typing import Any

from fastapi import status
from pydantic import BaseModel, Field
from store import Order, SortField

NOT_FOUND: dict[int | str, dict[str, Any]] = {status.HTTP_404_NOT_FOUND: {"description": "introuvable"}}


class PageQuery(BaseModel):
    q: str | None = None
    bucket: list[str] | None = None
    crawl: str | None = None
    run: str | None = None
    flagged_only: bool = False
    with_error: bool = False
    min_score: float | None = Field(default=None, ge=0, le=1)
    sort: SortField = "score"
    order: Order = "desc"
    page: int = Field(default=1, ge=1)
    size: int = Field(default=50, ge=1, le=500)


class PageRow(BaseModel):
    id: str
    url: str
    host: str | None
    bucket: str
    crawl: str
    score: float | None
    threshold: float | None
    flagged: bool
    error: str | None
    input_tokens: int | None
    output_tokens: int | None
    latency_ms: int | None
    analysed_at: datetime | None
    html_bytes: int
    fetched_at: datetime
    channels: list[str]


class PageList(BaseModel):
    items: list[PageRow]
    total: int
    flagged_total: int


class Usage(BaseModel):
    input_tokens: int | None
    output_tokens: int | None


class Detection(BaseModel):
    model: str
    state: str
    sent_chars: int | None
    saved_chars: int | None
    skipped_blocks: int | None
    skipped_reason: str | None
    truncated: bool
    answers: dict[str, Any] | None
    usage: Usage | None
    score: float | None
    threshold: float
    flagged: bool
    latency_ms: int | None
    error: str | None
    at: datetime
    channels: list[str]


class PageDetail(BaseModel):
    id: str
    url: str
    host: str | None
    bucket: str
    crawl: str
    headers: str
    html_bytes: int
    fetched_at: datetime
    detections: list[Detection]


class PageHtml(BaseModel):
    html: str


class PageRequest(BaseModel):
    request: dict[str, Any]


class Crawls(BaseModel):
    crawls: list[str]


class BucketCount(BaseModel):
    bucket: str
    count: int
    flagged: int


class Overview(BaseModel):
    stored: int
    analysed: int
    flagged: int
    runs: int
    input_tokens: int
    cost_usd: float
    threshold: float | None
    histogram: list[int]
    buckets: list[BucketCount]
    latest_flagged: list[PageRow]


class Run(BaseModel):
    id: str
    started_at: datetime
    model: str
    threshold: float
    analysed: int
    flagged: int
    errors: int
    input_tokens: int
    output_tokens: int
    cost_usd: float
    duration_ms: int
    median_latency_ms: float | None


class Daily(BaseModel):
    day: date
    analysed: int
    flagged_rate: float


class Runs(BaseModel):
    runs: list[Run]
    daily: list[Daily]
