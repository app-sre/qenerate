FROM registry.access.redhat.com/ubi9/python-39

ARG POETRY_VERSION
RUN pip install --upgrade pip && \
    pip install poetry==$POETRY_VERSION

# venv configuration
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

# other project related files
COPY README.md Makefile ./

# the source code
ARG CODE_ROOT
COPY $CODE_ROOT ./$CODE_ROOT
COPY tests ./tests
RUN poetry install --only-root

# run the Makefile target
ARG MAKE_TARGET
ARG TWINE_USERNAME
ARG TWINE_PASSWORD
RUN make $MAKE_TARGET
