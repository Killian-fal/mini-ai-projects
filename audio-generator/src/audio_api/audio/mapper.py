from audio_api.audio.dto import AudioResponseDTO, SegmentDTO, TranscriptDTO
from audio_api.transcript.model import TranscriptResult


def build_audio_response(
    transcript: TranscriptResult,
    trace_id: str,
    audio: str,
    audio_format: str,
) -> AudioResponseDTO:
    return AudioResponseDTO(
        transcript=map_transcript_to_dto(transcript),
        trace_id=trace_id,
        audio=audio,
        audio_format=audio_format,
    )


def map_transcript_to_dto(transcript: TranscriptResult) -> TranscriptDTO:
    return TranscriptDTO(
        segments=[
            SegmentDTO(
                text=segment["text"],
                start=segment["start"],
                end=segment["end"],
            )
            for segment in transcript.segments
        ],
        language=transcript.language,
        duration_seconds=transcript.duration_seconds,
    )
