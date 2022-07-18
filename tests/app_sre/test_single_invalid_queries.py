import json
import pytest
from qenerate.core.plugin import Plugin

from qenerate.plugins.pydantic_v1.plugin import (
    AnonymousQueryError,
    InvalidQueryError,
    PydanticV1Plugin,
)
from tests.util import get_introspection, get_query


def run_test(name: str, plugin: Plugin):
    with open(f"tests/app_sre/gql/single_invalid_queries/{name}.gql") as f:
        query = f.read()

    with open(f"tests/app_sre/gql/introspection.json") as f:
        schema = json.loads(f.read())["data"]

    result = plugin.generate_query_classes(
        query=query,
        fragments={},
        raw_schema=schema,
    )


def test_anonymous_query():
    name = "anonymous_query"
    with pytest.raises(AnonymousQueryError):
        run_test(
            name=name,
            plugin=PydanticV1Plugin(),
        )


def test_invalid_query():
    name = "invalid_query"
    with pytest.raises(InvalidQueryError):
        run_test(
            name=name,
            plugin=PydanticV1Plugin(),
        )
