.PHONY: setup test coverage ruff pylint

setup:
	python3.11 -m pip install poetry
	POETRY_VIRTUALENVS_IN_PROJECT=true poetry install --with=dev --no-root

test:
	PYTHONPATH=$(shell pwd) poetry run pytest

coverage:
	PYTHONPATH=$(shell pwd) poetry run pytest --cov=telegram_data_downloader --cov-report=term-missing

ruff:
	poetry run ruff check .

pylint:
	poetry run pylint --exit-zero telegram_data_downloader