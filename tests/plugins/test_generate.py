from pathlib import Path
import pytest
from qenerate.core.code_command import plugins
from qenerate.core.feature_flag_parser import FeatureFlags
from qenerate.core.plugin import GeneratedFile
from qenerate.core.preprocessor import GQLDefinition, GQLDefinitionType


@pytest.mark.parametrize(
    "case, dep_graph, type_map",
    [
        [
            "simple_queries",
            {},
            {
                "saas_file_simple": GQLDefinitionType.QUERY,
                "saas_file_reduced": GQLDefinitionType.QUERY,
                "saas_file_json": GQLDefinitionType.QUERY,
                "difficult_attribute_name": GQLDefinitionType.QUERY,
            },
        ],
        [
            "complex_queries",
            {},
            {
                "ocp_with_inline_fragments": GQLDefinitionType.QUERY,
                "saas_humongous": GQLDefinitionType.QUERY,
            },
        ],
        [
            "fragments",
            {},
            {
                "simple_fragment": GQLDefinitionType.FRAGMENT,
            },
        ],
    ],
)
@pytest.mark.parametrize("plugin_name", plugins.keys())
def test_rendering(
    schema,
    expected_files,
    case,
    dep_graph: dict[str, list[str]],
    type_map: dict[str, GQLDefinitionType],
    plugin_name,
):
    """Test code generation for each CASE x PLUGIN combination."""

    fragment_definitions = []
    query_definitions = []
    for source_file in Path(f"tests/generator/definitions/{case}").glob("**/*"):
        file_id = source_file.with_suffix("").name
        with open(source_file, "r") as f:
            content = f.read()
        kind = type_map[file_id]
        definition = GQLDefinition(
            feature_flags=FeatureFlags(plugin=plugin_name),
            source_file=source_file,
            definition=content,
            fragment_dependencies=dep_graph.get(file_id, []),
            kind=kind,
            name="",
        )
        if kind == GQLDefinitionType.QUERY:
            query_definitions.append(definition)
        else:
            fragment_definitions.append(definition)

    plugin = plugins[plugin_name]

    generated_files = []

    fragments = plugin.generate_fragments(
        definitions=fragment_definitions,
        schema=schema,
    )

    for fragment in fragments:
        generated_files.append(
            GeneratedFile(
                file=fragment.file,
                content=fragment.content,
            )
        )

    generated_files.extend(
        plugin.generate_queries(
            definitions=query_definitions,
            fragments=fragments,
            schema=schema,
        )
    )

    generated: list[GeneratedFile] = sorted(generated_files)
    expected: list[GeneratedFile] = sorted(
        expected_files(
            plugin=plugin_name,
            case=case,
        )
    )

    for i in range(len(generated)):
        # Helper to easier spot diffs in pytest output
        assert generated[i].content == expected[i].content

    assert generated == expected
