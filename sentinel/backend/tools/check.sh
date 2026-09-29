#!/bin/sh
set -e
cd "$(dirname "$0")/.."
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run tools/filelen.py
