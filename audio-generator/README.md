# Agent Audio API

Generates audio from a script, then transcribes it. FastAPI app on port `8000`.

## TTS Providers

Selected through `SELECT_PROVIDER` (`openai` or `gemini`).

### OpenAI
- Model `gpt-4o-mini-tts-2025-12-15`, voice `echo`, `wav` output.
- Requires `OPEN_API_KEY`.
- Docs: https://platform.openai.com/docs/guides/text-to-speech

### Gemini (Google Cloud Text-to-Speech)
- Model `gemini-3.1-flash-tts-preview`, voice `Puck`, language `fr-FR`.
- Requires `GOOGLE_APPLICATION_CREDENTIALS` (path to the service account JSON).
- Docs: https://cloud.google.com/text-to-speech/docs/gemini-tts

## Environment variables

| Variable | Details |
|---|---|
| `SELECT_PROVIDER` | `openai` or `gemini` |
| `OPEN_API_KEY` | OpenAI key (openai provider) |
| `GOOGLE_APPLICATION_CREDENTIALS` | path to the GCP JSON (gemini provider) |
| `ENABLE_MLFLOW` | `false` to run without an MLflow server (default `true`) |
| `MLFLOW_TRACKING_URI` | MLflow server URI (required if `ENABLE_MLFLOW=true`) |
| `MLFLOW_EXPERIMENT_NAME` | experiment name (required if `ENABLE_MLFLOW=true`) |
| `ENABLE_STORAGE_DEV` | `true` to write the audio into `audio/` (dev) |
| `MAX_CHUNK_CHARS` | max size of a chunk sent to the TTS (default `4000`) |

## Docker

```bash
# Build
docker build --platform linux/amd64 -t audio-api:latest .

# Run (OpenAI)
docker run --rm --platform linux/amd64 -p 8000:8000 \
  -e ENABLE_MLFLOW=false \
  -e SELECT_PROVIDER=openai \
  -e OPEN_API_KEY="sk-..." \
  audio-api:latest

# Run (Gemini) — mount the GCP JSON
docker run --rm -p 8000:8000 \
  -e ENABLE_MLFLOW=false \
  -e SELECT_PROVIDER=gemini \
  -v /path/to/creds.json:/secrets/gcp.json:ro \
  -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp.json \
  audio-api:latest
```
