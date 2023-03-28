from enum import Enum
from pathlib import Path
import pytest
from qenerate.core.code_command import plugins
from qenerate.core.feature_flag_parser import NamingCollisionStrategy, FeatureFlags
from qenerate.core.plugin import GeneratedFile
from qenerate.core.preprocessor import GQLDefinition, GQLDefinitionType


class Schema(Enum):
    APP_INTERFACE = "app-interface"
    APP_INTERFACE_2023_03 = "app-interface_2023_03"
    GITHUB = "github"


@pytest.mark.parametrize(
    "case, dep_graph, type_map, collision_strategies, use_schema, custom_type_mapping",
    [
        [
            "simple_queries",
            {},
            {
                "saas_file_simple": GQLDefinitionType.QUERY,
                "saas_file_reduced": GQLDefinitionType.QUERY,
                "saas_file_json": GQLDefinitionType.QUERY,
                "difficult_attribute_name": GQLDefinitionType.QUERY,
                "difficult_attribute_name_2": GQLDefinitionType.QUERY,
            },
            {},
            Schema.APP_INTERFACE,
            {},
        ],
        [
            "complex_queries",
            {},
            {
                "ocp_with_inline_fragments": GQLDefinitionType.QUERY,
                "enumerate_collisions": GQLDefinitionType.QUERY,
                "saas_humongous": GQLDefinitionType.QUERY,
            },
            {
                "enumerate_collisions": NamingCollisionStrategy.ENUMERATE,
            },
            Schema.APP_INTERFACE,
            {},
        ],
        [
            "fragments",
            {
                "nested_fragment": ["VaultSecret"],
                "multiple_nested_fragments": ["VaultSecret", "CommonJumphostFields"],
                "nested_layers": ["CommonJumphostFields"],
            },
            {
                "simple_fragment": GQLDefinitionType.FRAGMENT,
                "nested_fragment": GQLDefinitionType.FRAGMENT,
                "multiple_nested_fragments": GQLDefinitionType.FRAGMENT,
                "nested_layers": GQLDefinitionType.QUERY,
            },
            {},
            Schema.APP_INTERFACE,
            {},
        ],
        [
            "fragments_2023_03",
            {},
            {
                "fragment_with_inline": GQLDefinitionType.FRAGMENT,
            },
            {},
            Schema.APP_INTERFACE_2023_03,
            {},
        ],
        [
            "simple_queries_with_fragments",
            {
                "ocp_query": ["VaultSecret"],
                "ocp_query_partial": ["VaultSecretPartial"],
                "ocp_query_multiple": ["VaultSecretPartial", "VaultSecretVersion"],
            },
            {
                "vault_secret_partial_fragment": GQLDefinitionType.FRAGMENT,
                "vault_secret_fragment": GQLDefinitionType.FRAGMENT,
                "vault_secret_version_fragment": GQLDefinitionType.FRAGMENT,
                "ocp_query": GQLDefinitionType.QUERY,
                "ocp_query_partial": GQLDefinitionType.QUERY,
                "ocp_query_multiple": GQLDefinitionType.QUERY,
            },
            {},
            Schema.APP_INTERFACE,
            {},
        ],
        [
            "complex_queries_with_fragments",
            {
                "saas_with_multiple_fragment_references": ["VaultSecret"],
            },
            {
                "vault_secret_fragment": GQLDefinitionType.FRAGMENT,
                "saas_with_multiple_fragment_references": GQLDefinitionType.QUERY,
            },
            {},
            Schema.APP_INTERFACE,
            {},
        ],
        [
            "github",
            {},
            {
                "invitations_enum": GQLDefinitionType.QUERY,
                "issues_datetime_html": GQLDefinitionType.QUERY,
                "comment_mutation": GQLDefinitionType.MUTATION,
            },
            {},
            Schema.GITHUB,
            {},
        ],
        [
            "custom_mappings",
            {},
            {
                "saas_file_json": GQLDefinitionType.QUERY,
            },
            {},
            Schema.APP_INTERFACE,
            {"JSON": "str"},
        ],
    ],
)
@pytest.mark.parametrize("plugin_name", plugins.keys())
def test_rendering(
    use_schema,
    app_interface_schema,
    app_interface_2023_03_schema,
    github_schema,
    expected_files,
    case,
    dep_graph: dict[str, list[str]],
    type_map: dict[str, GQLDefinitionType],
    collision_strategies: dict[str, NamingCollisionStrategy],
    plugin_name,
    custom_type_mapping,
):
    """Test code generation for each CASE x PLUGIN combination."""
    schema = app_interface_schema
    if use_schema == Schema.GITHUB:
        schema = github_schema
    elif use_schema == Schema.APP_INTERFACE_2023_03:
        schema = app_interface_2023_03_schema
    fragment_definitions = []
    operation_definitions = []
    for source_file in Path(f"tests/generator/definitions/{case}").glob("**/*"):
        file_id = source_file.with_suffix("").name
        with open(source_file, "r") as f:
            content = f.read()
        kind = type_map[file_id]
        collision_strategy = collision_strategies.get(
            file_id, NamingCollisionStrategy.PARENT_CONTEXT
        )
        definition = GQLDefinition(
            feature_flags=FeatureFlags(
                plugin=plugin_name,
                gql_scalar_mappings=custom_type_mapping,
                collision_strategy=collision_strategy,
            ),
            source_file=source_file,
            definition=content,
            fragment_dependencies=dep_graph.get(file_id, []),
            kind=kind,
            name=file_id,
        )
        if kind == GQLDefinitionType.FRAGMENT:
            fragment_definitions.append(definition)
        else:
            operation_definitions.append(definition)

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
        plugin.generate_operations(
            definitions=operation_definitions,
            fragments=fragments,
            schema=schema,
        )
    )

    generated: list[GeneratedFile] = sorted(generated_files, key=lambda x: x.file)
    expected: list[GeneratedFile] = sorted(
        expected_files(
            plugin=plugin_name,
            case=case,
        ),
        key=lambda x: x.file,
    )

    for i in range(len(generated)):
        # Helper to easier spot diffs in pytest output
        assert generated[i].content == expected[i].content

    assert generated == expected
