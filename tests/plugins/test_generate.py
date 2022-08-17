from pathlib import Path
import pytest
from qenerate.core.code_command import plugins
from qenerate.core.feature_flag_parser import FeatureFlags
from qenerate.core.plugin import AnonymousQueryError, InvalidQueryError
from qenerate.core.preprocessor import GQLDefinition, GQLDefinitionType


@pytest.mark.parametrize(
    "query",
    [
        "saas_file_simple",
        "complex_inline_fragments_and_collisions",
        "saas_humongous",
        "difficult_attribute_name",
        "ocp_with_inline_fragments",
        "saas_file_json",
    ],
)
@pytest.mark.parametrize("plugin_name", plugins.keys())
def test_generate(schema_raw, expected_files, query, plugin_name):
    """Test code generation for each QUERY x PLUGIN combinations."""
    source_file = Path(f"tests/queries/{query}.gql")
    with open(source_file, "r") as f:
        content = f.read()
    plugin = plugins[plugin_name]
    definition = GQLDefinition(
        feature_flags=FeatureFlags(plugin=plugin_name),
        source_file=source_file,
        definition=content,
        kind=GQLDefinitionType.QUERY,
        name="",
    )
    generated_files = plugin.generate(definition=definition, raw_schema=schema_raw)
    assert generated_files == expected_files(plugin=plugin_name, query=query)


@pytest.mark.parametrize(
    "query, exception",
    [
        ["anonymous_query", AnonymousQueryError],
        ["invalid_query", InvalidQueryError],
    ],
)
@pytest.mark.parametrize("plugin_name", plugins.keys())
def test_invalid_queries(schema_raw, query, exception, plugin_name):
    source_file = Path(f"tests/queries/{query}.gql")
    plugin = plugins[plugin_name]

    with open(source_file, "r") as f:
        content = f.read()

    plugin = plugins[plugin_name]
    definition = GQLDefinition(
        feature_flags=FeatureFlags(plugin=plugin_name),
        source_file=source_file,
        definition=content,
        kind=GQLDefinitionType.QUERY,
        name="",
    )
    with pytest.raises(exception):
        plugin.generate(definition=definition, raw_schema=schema_raw)
