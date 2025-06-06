FROM registry.access.redhat.com/ubi9/python-39
COPY --from=ghcr.io/astral-sh/uv:0.7.11@sha256:d7e699d374d4e5cb52a37d5c8f0ee15e3c7572850325953bf9fa8d781cfa92fc /uv /bin/uv

ENV \
    # use venv from ubi image
    UV_PROJECT_ENVIRONMENT=$APP_ROOT \
    # compile bytecode for faster startup
    UV_COMPILE_BYTECODE="true" \
    # disable uv cache. it doesn't make sense in a container
    UV_NO_CACHE=true

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --python /usr/bin/python3

# other project related files
COPY LICENSE README.md Makefile ./

# the source code
COPY qenerate ./qenerate
COPY --chown=1001:0 tests ./tests
RUN uv sync --frozen --no-editable

# run the Makefile target
ARG MAKE_TARGET
ARG TWINE_USERNAME
ARG TWINE_PASSWORD
RUN make $MAKE_TARGET
