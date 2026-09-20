import mlflow
from fastapi import APIRouter

from audio_api.audio.audio_service import generate_audio
from audio_api.audio.dto import AudioRequestDTO, AudioResponseDTO
from audio_api.audio.mapper import build_audio_response
from audio_api.environment import ENABLE_STORAGE_DEV
from audio_api.storage.storage_service import store_audio_locally
from audio_api.transcript.transcript_service import transcript_audio

audio_router = APIRouter()


@audio_router.post("/audio/process", response_model=AudioResponseDTO)
async def process_audio(request: AudioRequestDTO) -> AudioResponseDTO:
    with mlflow.start_span(name="process_audio") as span:
        span.set_inputs(request)

        audio, audio_format, audio_bytes = generate_audio(request.script)

        if ENABLE_STORAGE_DEV:
            store_audio_locally(audio_bytes, audio_format)

        transcript = transcript_audio(
            audio_date=audio_bytes,
            script=request.script,
            lang=request.lang,
        )

        response = build_audio_response(
            transcript=transcript,
            trace_id=span.trace_id,
            audio=audio,
            audio_format=audio_format,
        )

        span.set_outputs(response)

        return response
