# Sentinel — backend

```sh
uv sync --all-packages
docker compose up -d
uv run --env-file .env uvicorn api.main:app --reload --port 8000
```