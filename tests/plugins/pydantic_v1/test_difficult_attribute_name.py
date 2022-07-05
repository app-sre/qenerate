from qenerate.plugins.pydantic_v1.plugin import PydanticV1Plugin
from tests.util import get_introspection, get_query, get_result


def test_difficult_attribute_name_query():
    schema_raw = get_introspection()
    query = get_query("difficult_attribute_name.gql")
    plugin = PydanticV1Plugin()
    result = plugin.generate(query=query, raw_schema=schema_raw)
    assert result == get_result(
        plugin="pydantic_v1",
        filename="difficult_attribute_name.py.txt",
    )
