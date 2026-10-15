.PHONY: install format check test eval

install:
	uv sync --all-packages

format:
	uv run ruff format

check:
	uv run ruff check
	uv run pyright

test:
	uv run pytest -p interactive_support_flow_test.coverage.plugin

eval:
	uv run --env-file .env pytest -m eval -rP
