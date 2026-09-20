import base64

import mlflow
from mlflow.entities import SpanType

from audio_api.audio.chunk_service import text_to_chunks
from audio_api.audio.concatenante_wav_service import concatenate_wav_segments
from audio_api.audio.provider.gemini import generate_gemini_audio
from audio_api.audio.provider.openai import generate_openai_audio
from audio_api.audio.provider.provider import OPENAI_PROVIDER, GEMINI_PROVIDER
from audio_api.environment import SELECT_PROVIDER


DEFAULT_INSTRUCTIONS = (
    "Generate a high-quality audio clip in French with the following requirements:\n"
    "- Apply appropriate intonation and emphasis to enhance listener engagement.\n"
)


def generate_audio(text: str) -> tuple[str, str, bytes]:
    with mlflow.start_span("generate_audio", span_type=SpanType.CHAIN) as span:
        span.set_inputs(text)

        chunks = text_to_chunks(text, DEFAULT_INSTRUCTIONS)
        if not chunks:
            raise ValueError(
                "No text provided for audio generation after normalization."
            )

        if SELECT_PROVIDER == OPENAI_PROVIDER:
            audio_segments = generate_openai_audio(chunks, DEFAULT_INSTRUCTIONS)
        elif SELECT_PROVIDER == GEMINI_PROVIDER:
            audio_segments = generate_gemini_audio(chunks, text, DEFAULT_INSTRUCTIONS)
        else:
            raise ValueError("Invalid provider")

        combined_audio = concatenate_wav_segments(audio_segments)
        encoded = base64.b64encode(combined_audio).decode("utf-8")

        span.set_outputs({"audio_size": len(encoded), "format": "wav"})

        # Encoded in wav
        return encoded, "wav", combined_audio
