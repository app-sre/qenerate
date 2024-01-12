.PHONY: venv format setup.py test

venv:
	poetry config --local virtualenvs.in-project true
	poetry install
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install poetry2setup

format:
	poetry run ruff format
	poetry run ruff check

setup.py:
	. .venv/bin/activate && poetry2setup > setup.py

test:
	poetry run pytest -vv
	poetry run ruff format --check
	poetry run ruff check --no-fix
	poetry run mypy qenerate
