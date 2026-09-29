from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Chunk:
    channel: str
    text: str
