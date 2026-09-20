import gc
import whisperx
import librosa
import io
import soundfile as sf
import numpy as np
import mlflow
import torch

from mlflow.entities import SpanType
from audio_api.transcript.model import TranscriptResult

# Maybe use ctc-forced-aligner if whisperx not good
def transcript_audio(audio_date: bytes, script: str, lang: str) -> TranscriptResult:
    with mlflow.start_span("transcript_audio", span_type=SpanType.CHAIN) as span:
        span.set_inputs(
            {
                "audio_size": len(audio_date),
                "script": script,
                "language": lang,
            }
        )

        model_whisperx, metadata = whisperx.load_align_model(
            language_code=lang, device=_pick_device()
        )

        audio_data = _load_audio_from_bytes(audio_date)

        audio_duration = len(audio_data) / 16000.0
        transcript_existant = [
            {
                "text": script,
                "start": 0.0,
                "end": audio_duration,
            }
        ]

        aligned = whisperx.align(
            transcript_existant,
            model_whisperx,
            metadata,
            audio_data,
            _pick_device(),
            return_char_alignments=False,
        )

        segments = []
        for seg in aligned["segments"]:
            seg_copy = dict(seg)
            seg_copy.pop("words", None)
            segments.append(seg_copy)

        result = TranscriptResult(
            segments=segments,
            language=lang,
            duration_seconds=audio_duration,
        )
        span.set_outputs(result)

        del model_whisperx
        gc.collect()

        return result


def _load_audio_from_bytes(wav_bytes):
    audio, sr = sf.read(io.BytesIO(wav_bytes))
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)
    audio = audio.astype("float32")
    if sr != 16000:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
    return audio

def _pick_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"