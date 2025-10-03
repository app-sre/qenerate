CONTAINER_ENGINE ?= $(shell which podman >/dev/null 2>&1 && echo podman || echo docker)

format:
	uv run ruff check
	uv run ruff format
.PHONY: format

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

pypi:
	uv build
	uv publish || true
.PHONY: pypi
