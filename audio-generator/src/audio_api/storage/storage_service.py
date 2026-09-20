from datetime import datetime, timezone
from pathlib import Path

import mlflow
from mlflow.entities import SpanType

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_AUDIO_DIR = _PROJECT_ROOT / "audio-files"


@mlflow.trace(name="store_audio_locally", span_type=SpanType.CHAIN)
def store_audio_locally(audio_bytes: bytes, audio_format: str = "wav") -> str:
    _AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    file_path = _AUDIO_DIR / f"audio_{timestamp}.{audio_format}"
    file_path.write_bytes(audio_bytes)

    return str(file_path)
