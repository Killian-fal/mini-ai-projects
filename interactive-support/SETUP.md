# Setup

## Requirements

- [uv](https://docs.astral.sh/uv/) (Python 3.13)
- Docker, for MLflow
- Node 24 and pnpm 12, for the web front

## Setup

```bash
make install           # Python workspace
docker compose up -d   # MLflow on http://localhost:5001
cp .env.example .env
```

Fill in `.env`:

```dotenv
TYPESAFE_API_KEY=...
OPENROUTER_API_KEY=...
MLFLOW_TRACKING_URI=http://localhost:5001
API_PORT=5002
```

## Run the CLI

```bash
uv run cli
```

It plays a whole conversation in the terminal with the real models. The first message is set in
`packages/cli/src/interactive_support_cli/main.py`.

## Run the back and the front

```bash
uv run api             # API on http://localhost:5002
```

```bash
cd frontend
pnpm install
pnpm dev               # http://localhost:5173
```

The front calls `http://localhost:5002` unless `VITE_API_URL` says otherwise.

Demo orders: `CMA_001` (not prepared), `CMA_002` (in preparation), `CMA_003` (shipped), `CMA_004` (delivered).
