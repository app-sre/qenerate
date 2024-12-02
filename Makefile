# TWINE_USERNAME & TWINE_PASSWORD are available in the Jenkins job
BUILD_ARGS := TWINE_USERNAME TWINE_PASSWORD
CONTAINER_ENGINE ?= $(shell which podman >/dev/null 2>&1 && echo podman || echo docker)

.EXPORT_ALL_VARIABLES:
UV_PUBLISH_USERNAME = $(TWINE_USERNAME)
UV_PUBLISH_PASSWORD = $(TWINE_PASSWORD)

format:
	uv run ruff check
	uv run ruff format
.PHONY: format

pr-check:
	$(CONTAINER_ENGINE) build --build-arg MAKE_TARGET=test $(foreach arg,$(BUILD_ARGS),--build-arg $(arg)) .
.PHONY: pr-check

test:
	uv run ruff check --no-fix
	uv run ruff format --check
	uv run mypy
	uv run pytest -vv

	# test pypi package build
	uv build

	# test dist/qenerate-*.tar.gz is not empty
	[ -s dist/qenerate-*.tar.gz ] || (echo "dist/qenerate-*.tar.gz is empty" && exit 1)

	# test dist/qenerate-*.tar.gz exactly has 19 files. We don't want to publish other files to pypi.
	[ $$(tar -tzf dist/qenerate-*.tar.gz | wc -l) -eq 18 ] || (tar -tzf dist/qenerate-*.tar.gz && echo "dist/qenerate-*.tar.gz has more or less than 18 files" && exit 1)

	# test dist/qenerate-*.whl is not empty
	[ -s dist/qenerate-*.whl ] || (echo "dist/qenerate-*.whl is empty" && exit 1)

	# test dist/qenerate-*.whl exactly has 24 files. We don't want to publish other files to pypi.
	[ $$(unzip -l dist/qenerate-*.whl | wc -l) -eq 24 ] || (unzip -l dist/qenerate-*.whl && echo "dist/qenerate-*.whl has more or less than 24 files" && exit 1)
.PHONY: test

build-deploy:
	$(CONTAINER_ENGINE) build --build-arg MAKE_TARGET=pypi $(foreach arg,$(BUILD_ARGS),--build-arg $(arg)) .
.PHONY: build-deploy

pypi:
	uv build
	uv publish
.PHONY: pypi
