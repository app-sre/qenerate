FROM registry.access.redhat.com/ubi9/python-314@sha256:f434cebb0d9f30e7dbea83df2b1ef7906b2e39586b7d5de82c172fd50f67cdc9 AS test
COPY --from=ghcr.io/astral-sh/uv:0.11.24@sha256:99ea34acedc870ba4ad11a1f540a1c04267c9f30aadc465a94406f52dfda2c36 /uv /bin/uv
COPY LICENSE /licenses/

ENV \
    # use venv from ubi image
    UV_PROJECT_ENVIRONMENT=$APP_ROOT \
    # disable uv cache. it doesn't make sense in a container
    UV_NO_CACHE=true

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# other project related files
COPY LICENSE README.md Makefile ./

# the source code
COPY qenerate ./qenerate
COPY --chown=1001:0 tests ./tests
RUN uv sync --frozen --no-editable

RUN make test

#
# PyPI publish image
#
FROM test AS pypi
# Secrets are owned by root and are not readable by others :(
USER root
RUN --mount=type=secret,id=app-sre-pypi-credentials/token UV_PUBLISH_TOKEN=$(cat /run/secrets/app-sre-pypi-credentials/token) make pypi
USER 1001
