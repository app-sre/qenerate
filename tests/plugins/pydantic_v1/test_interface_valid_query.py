from qenerate.plugins.pydantic_v1.plugin import PydanticV1Plugin
from tests.util import get_introspection, get_result


def test_interface_valid_query():
    schema_raw = get_introspection()
    query_file = "tests/queries/ocp_with_inline_fragments.gql"
    plugin = PydanticV1Plugin()
    result = plugin.generate(query_file=query_file, raw_schema=schema_raw)
    assert result == get_result(
        plugin="pydantic_v1",
        filename="ocp_with_inline_fragments.py.txt",
    )
