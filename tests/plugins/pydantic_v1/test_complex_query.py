from qenerate.plugins.pydantic_v1.plugin import PydanticV1Plugin
from tests.util import get_introspection, get_result


def test_interface_valid_query():
    schema_raw = get_introspection()
    query_file = "tests/queries/complex_inline_fragments_and_collisions.gql"
    plugin = PydanticV1Plugin()
    result = plugin.generate(query_file=query_file, raw_schema=schema_raw)
    assert result == get_result(
        plugin="pydantic_v1",
        filename="complex_inline_fragments_and_collisions.py.txt",
    )


def test_interface_humongous_query():
    schema_raw = get_introspection()
    query_file = "tests/queries/saas_humongous.gql"
    plugin = PydanticV1Plugin()
    result = plugin.generate(query_file=query_file, raw_schema=schema_raw)
    assert result == get_result(
        plugin="pydantic_v1",
        filename="saas_humongous.py.txt",
    )
