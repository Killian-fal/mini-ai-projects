import mlflow
from mlflow.entities import SpanType

from audio_api.audio.chunk_service import text_to_chunks
from audio_api.llm import OPENAI_CLIENT


def generate_openai_audio(chunks: list[str], instructions: str) -> list[bytes]:
    return [_generate_openai_audio_chunk(chunk, instructions) for chunk in chunks]


# Documentation and Try : https://developers.openai.com/api/docs/models/gpt-4o-mini-tts
@mlflow.trace(name="generate_openai_audio_chunk", span_type=SpanType.CHAIN)
def _generate_openai_audio_chunk(text: str, instructions: str) -> bytes:
    response = OPENAI_CLIENT.audio.speech.create(
        model="gpt-4o-mini-tts-2025-12-15",
        voice="echo",
        input=text,
        instructions=instructions,
        response_format="wav",
    )
    return response.content
