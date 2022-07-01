.PHONY: venv format setup.py test

venv:
	poetry config --local virtualenvs.in-project true
	poetry install
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install poetry2setup

format:
	poetry run black qenerate tests

setup.py:
	. .venv/bin/activate && poetry2setup > setup.py
	
test:
	poetry run pytest -vv
	poetry run flake8 qenerate
	poetry run mypy qenerate
	poetry run black --check qenerate tests
