from qenerate.plugins.pydantic_v1.plugin import PydanticV1Plugin
from tests.util import get_introspection, get_query, get_result


def test_simple_valid_query():
    schema_raw = get_introspection()
    query = get_query("saas_file_simple.gql")
    plugin = PydanticV1Plugin()
    result = plugin.generate(query=query, raw_schema=schema_raw)
    assert result == get_result(
        plugin="pydantic_v1", filename="saas_file_simple.py.txt"
    )
