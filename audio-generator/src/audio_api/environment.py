import os

OPEN_API_KEY_ENV = os.environ.get("OPEN_API_KEY")
GOOGLE_APPLICATION_CREDENTIALS_ENV = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
SELECT_PROVIDER = os.environ.get("SELECT_PROVIDER", "none") # openai or gemini

# Maximum size (in characters) of a text chunk sent to TTS.
# The OpenAI audio.speech API limits `input` to 4,096 characters: we stay below that limit.
MAX_CHUNK_CHARS = int(os.environ.get("MAX_CHUNK_CHARS", 4000))

# Stores the generated audio locally (in the `audio/` folder at the root). For dev only.
ENABLE_STORAGE_DEV = os.environ.get("ENABLE_STORAGE_DEV", "false").lower() == "true"

ENABLE_MLFLOW = os.environ.get("ENABLE_MLFLOW", "true").lower() == "true"
MLFLOW_TRACKING_URI_ENV = os.environ.get("MLFLOW_TRACKING_URI")
MLFLOW_EXPERIMENT_NAME_ENV = os.environ.get("MLFLOW_EXPERIMENT_NAME")
