from pathlib import Path
import pytest
from qenerate.core.code_command import plugins
from qenerate.core.feature_flag_parser import FeatureFlags
from qenerate.core.plugin import AnonymousQueryError, InvalidQueryError
from qenerate.core.preprocessor import GQLDefinition, GQLDefinitionType


@pytest.mark.parametrize(
    "definition, exception",
    [
        ["anonymous_query", AnonymousQueryError],
        ["invalid_query", InvalidQueryError],
    ],
)
@pytest.mark.parametrize("plugin_name", plugins.keys())
def test_exceptions(schema, definition, exception, plugin_name):
    source_file = Path(f"tests/generator/definitions/exceptions/{definition}.gql")
    plugin = plugins[plugin_name]

    with open(source_file, "r") as f:
        content = f.read()

    plugin = plugins[plugin_name]
    definition = GQLDefinition(
        feature_flags=FeatureFlags(plugin=plugin_name),
        source_file=source_file,
        definition=content,
        kind=GQLDefinitionType.QUERY,
        fragment_dependencies=[],
        name="",
    )
    with pytest.raises(exception):
        plugin.generate_queries(definitions=[definition], fragments=[], schema=schema)
