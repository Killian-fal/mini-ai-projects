from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Self

RUN_ID_FORMAT = "%Y-%m-%dT%H:%M"


@dataclass(frozen=True, slots=True)
class RunKey:
    """A run is a group of detections sharing (minute, model, threshold)."""

    minute: datetime
    model: str
    threshold: float

    @property
    def id(self) -> str:
        return f"{self.minute:{RUN_ID_FORMAT}}|{self.model}|{self.threshold}"

    @classmethod
    def parse(cls, run_id: str) -> Self | None:
        try:
            minute, model, threshold = run_id.split("|")
            return cls(datetime.strptime(minute, RUN_ID_FORMAT).replace(tzinfo=UTC), model, float(threshold))
        except ValueError:
            return None


@dataclass(frozen=True, slots=True)
class Run:
    key: RunKey
    analysed: int
    flagged: int
    errors: int
    input_tokens: int
    output_tokens: int
    duration_ms: int
    median_latency_ms: float | None


@dataclass(frozen=True, slots=True)
class DayCount:
    day: date
    analysed: int
    flagged: int
