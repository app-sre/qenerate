import pytest

from qenerate.plugins.pydantic_v1.plugin import (
    AnonymousQueryError,
    InvalidQueryError,
    PydanticV1Plugin,
)
from tests.util import get_introspection


def test_anonymous_query():
    schema_raw = get_introspection()
    query_file = "tests/queries/anonymous_query.gql"
    plugin = PydanticV1Plugin()
    with pytest.raises(AnonymousQueryError):
        plugin.generate(query_file=query_file, raw_schema=schema_raw)


def test_invalid_query():
    schema_raw = get_introspection()
    query_file = "tests/queries/invalid_query.gql"
    plugin = PydanticV1Plugin()
    with pytest.raises(InvalidQueryError):
        plugin.generate(query_file=query_file, raw_schema=schema_raw)
