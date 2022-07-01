FROM registry.access.redhat.com/ubi8/python-39

# TODO: remove root
USER root
COPY . .

RUN pip install --upgrade pip && \
    pip install poetry==1.1.13
RUN make venv
RUN make test
