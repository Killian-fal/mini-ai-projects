from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Usage:
    input_tokens: int | None
    output_tokens: int | None


@dataclass(frozen=True, slots=True)
class Reply:
    model: str
    answers: dict[str, Any]
    usage: Usage | None
    request: str
