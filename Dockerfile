FROM registry.access.redhat.com/ubi9/python-312@sha256:558341c02c51ee12820185b203edaa953f18d1c2ac4426947547edd9cea44ff0 AS test
COPY --from=ghcr.io/astral-sh/uv:0.9.2@sha256:6dbd7c42a9088083fa79e41431a579196a189bcee3ae68ba904ac2bf77765867 /uv /bin/uv
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
