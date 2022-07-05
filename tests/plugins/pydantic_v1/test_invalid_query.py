import pytest

from qenerate.plugins.pydantic_v1.plugin import (
    AnonymousQueryError,
    InvalidQueryError,
    PydanticV1Plugin,
)
from tests.util import get_introspection, get_query


def test_anonymous_query():
    schema_raw = get_introspection()
    query = get_query("anonymous_query.gql")
    plugin = PydanticV1Plugin()
    with pytest.raises(AnonymousQueryError):
        plugin.generate(query=query, raw_schema=schema_raw)


def test_invalid_query():
    schema_raw = get_introspection()
    query = get_query("invalid_query.gql")
    plugin = PydanticV1Plugin()
    with pytest.raises(InvalidQueryError):
        plugin.generate(query=query, raw_schema=schema_raw)
