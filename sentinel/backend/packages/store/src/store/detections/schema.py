import zlib
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Self

from store.connection import Document


@dataclass(frozen=True, slots=True)
class Usage:
    input_tokens: int | None
    output_tokens: int | None


@dataclass(frozen=True, slots=True)
class Detection:
    model: str
    state: str
    channels: list[str]
    score: float | None
    threshold: float
    flagged: bool
    at: datetime
    error: str | None = None
    request: str | None = None
    answers: dict[str, Any] | None = None
    usage: Usage | None = None
    latency_ms: int | None = None
    truncated: bool = False
    sent_chars: int | None = None
    saved_chars: int | None = None
    skipped_blocks: int | None = None
    skipped_reason: str | None = None

    def to_doc(self) -> Document:
        return {
            **asdict(self),
            "state": zlib.compress(self.state.encode()),
            "request": None if self.request is None else zlib.compress(self.request.encode()),
        }

    @classmethod
    def from_doc(cls, doc: Document) -> Self:
        request, usage = doc.get("request"), doc.get("usage")
        return cls(
            **{
                **doc,
                "state": zlib.decompress(doc["state"]).decode(),
                "request": None if request is None else zlib.decompress(request).decode(),
                "usage": None
                if usage is None
                else Usage(usage.get("input_tokens"), usage.get("output_tokens")),
            }
        )
