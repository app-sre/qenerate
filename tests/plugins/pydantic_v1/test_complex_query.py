from qenerate.plugins.pydantic_v1.plugin import PydanticV1Plugin
from tests.util import get_introspection, get_query, get_result


def test_interface_valid_query():
    schema_raw = get_introspection()
    query = get_query(filename="complex_inline_fragments_and_collisions.gql")
    plugin = PydanticV1Plugin()
    result = plugin.generate(query=query, raw_schema=schema_raw)
    assert result == get_result(
        plugin="pydantic_v1",
        filename="complex_inline_fragments_and_collisions.py.txt",
    )
