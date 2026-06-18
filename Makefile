.PHONY: install ingest test lint format

install:
	poetry install

ingest:
	poetry run python ingestion/sncf_api.py

test:
	poetry run pytest tests/

lint:
	poetry run ruff check .

format:
	poetry run ruff format .
