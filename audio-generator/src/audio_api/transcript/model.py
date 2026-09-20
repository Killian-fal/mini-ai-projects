import dataclasses
from typing import Any


@dataclasses.dataclass
class TranscriptResult:
    segments: list[Any]
    language: str
    duration_seconds: float
