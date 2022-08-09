from qenerate.core.code_command import plugins
import pytest
from qenerate.plugins.pydantic_v1.plugin import AnonymousQueryError, InvalidQueryError


@pytest.mark.parametrize(
    "query",
    [
        # simple query
        "saas_file_simple",
        # interface query
        "complex_inline_fragments_and_collisions",
        # interface humongous query
        "saas_humongous",
        # difficult attribute name query
        "difficult_attribute_name",
        # inline fragments
        "ocp_with_inline_fragments",
        # json query
        "saas_file_json",
    ],
)
@pytest.mark.parametrize("plugin_name", plugins.keys())
def test_generate(schema_raw, expected_files, query, plugin_name):
    """Test code generation for each QUERY x PLUGIN combinations."""
    query_file = f"tests/queries/{query}.gql"
    plugin = plugins[plugin_name]
    generated_files = plugin.generate(query_file=query_file, raw_schema=schema_raw)
    assert generated_files == expected_files(plugin=plugin_name, query=query)


@pytest.mark.parametrize(
    "query, exception",
    [
        # anonymous query
        ["anonymous_query", AnonymousQueryError],
        # invalid query
        ["invalid_query", InvalidQueryError],
    ],
)
@pytest.mark.parametrize("plugin_name", plugins.keys())
def test_invalid_queries(schema_raw, query, exception, plugin_name):
    query_file = f"tests/queries/{query}.gql"
    plugin = plugins[plugin_name]
    with pytest.raises(exception):
        plugin.generate(query_file=query_file, raw_schema=schema_raw)
