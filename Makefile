venv:
	poetry config virtualenvs.in-project true
	poetry install

format:
	poetry run black qenerate tests

test:
	poetry run pytest
	poetry run flake8 qenerate
	poetry run mypy qenerate
	poetry run black --check qenerate tests
