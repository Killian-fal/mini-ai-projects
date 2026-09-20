from typing import Annotated

from pydantic import BaseModel, StringConstraints


class AudioRequestDTO(BaseModel):
    script: str
    lang: Annotated[str, StringConstraints(pattern=r"^[a-z]{2}$")]


class SegmentDTO(BaseModel):
    start: float
    end: float
    text: str


class TranscriptDTO(BaseModel):
    segments: list[SegmentDTO]
    language: str
    duration_seconds: float


class AudioResponseDTO(BaseModel):
    transcript: TranscriptDTO
    trace_id: str
    audio: str
    audio_format: str
