import re

import mlflow
from mlflow.entities import SpanType

from audio_api.audio.chunk_service import text_to_chunks
from audio_api.audio.provider.provider import GEMINI_PROVIDER
from audio_api.environment import SELECT_PROVIDER, GOOGLE_APPLICATION_CREDENTIALS_ENV

if SELECT_PROVIDER == GEMINI_PROVIDER and not GOOGLE_APPLICATION_CREDENTIALS_ENV:
    raise EnvironmentError(
        "GOOGLE_APPLICATION_CREDENTIALS environment variable is not set."
    )

def generate_gemini_audio(chunks: list[str], text: str, instructions: str) -> list[bytes]:
    from google.api_core.exceptions import InvalidArgument

    try:
        audio_segments = [
            _generate_gemini_audio_chunk(chunk, instructions) for chunk in chunks
        ]
    except InvalidArgument as e:
        match = re.search(r"The total size must be less than (\d+) bytes", str(e))
        if match:
            adjusted_limit = int(match.group(1)) - 200
            retry_chunks = text_to_chunks(text, instructions, adjusted_limit)
            audio_segments = [
                _generate_gemini_audio_chunk(chunk, instructions)
                for chunk in retry_chunks
            ]
        else:
            raise Exception(f"TTS synthesis failed: {e}") from e

    return audio_segments


# Documentation : https://cloud.google.com/text-to-speech/docs/gemini-tts?hl=fr
# Try : https://cloud.google.com/text-to-speech?hl=fr
@mlflow.trace(name="generate_gemini_audio_chunk", span_type=SpanType.CHAIN)
def _generate_gemini_audio_chunk(text: str, instructions: str) -> bytes:
    from google.cloud import texttospeech

    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text, prompt=instructions)

    voice = texttospeech.VoiceSelectionParams(
        language_code="fr-FR",
        name="Achird",
        model_name="gemini-3.1-flash-tts-preview",
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    return response.audio_content
