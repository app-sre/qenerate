CODE_ROOT := qenerate
# TWINE_USERNAME & TWINE_PASSWORD are available in the Jenkins job
BUILD_ARGS := CODE_ROOT=$(CODE_ROOT) POETRY_VERSION=1.8.3 TWINE_USERNAME TWINE_PASSWORD
CONTAINER_ENGINE ?= $(shell which podman >/dev/null 2>&1 && echo podman || echo docker)

.EXPORT_ALL_VARIABLES:
POETRY_HTTP_BASIC_PYPI_USERNAME = $(TWINE_USERNAME)
POETRY_HTTP_BASIC_PYPI_PASSWORD = $(TWINE_PASSWORD)

format:
	poetry run ruff check
	poetry run ruff format
.PHONY: format

pr-check:
	$(CONTAINER_ENGINE) build --build-arg MAKE_TARGET=test $(foreach arg,$(BUILD_ARGS),--build-arg $(arg)) .
.PHONY: pr-check

test:
	poetry run ruff check --no-fix
	poetry run ruff format --check
	poetry run mypy
	poetry run pytest -vv
.PHONY: test

build-deploy:
	$(CONTAINER_ENGINE) build --build-arg MAKE_TARGET=pypi $(foreach arg,$(BUILD_ARGS),--build-arg $(arg)) .
.PHONY: build-deploy

pypi:
	poetry publish --build --skip-existing
.PHONY: pypi
