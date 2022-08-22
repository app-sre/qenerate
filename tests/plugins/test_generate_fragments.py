from pathlib import Path
import pytest

from qenerate.core.code_command import plugins
from qenerate.core.feature_flag_parser import FeatureFlags
from qenerate.core.plugin import Fragment, GeneratedFile
from qenerate.core.preprocessor import GQLDefinitionType, GQLDefinition


@pytest.mark.parametrize(
    "fragment, class_name, import_path, fragment_name",
    [
        [
            "simple_fragment",
            "VaultSecret",
            "tests.fragments.simple_fragment",
            "Vault_Secret",
        ],
    ],
)
@pytest.mark.parametrize("plugin_name", plugins.keys())
def test_generate(
    schema,
    expected_files,
    fragment,
    class_name,
    import_path,
    fragment_name,
    plugin_name,
):
    """Test code generation for each FRAGMENT x PLUGIN combinations."""
    source_file = Path(f"tests/fragments/{fragment}.gql")
    with open(source_file, "r") as f:
        content = f.read()
    plugin = plugins[plugin_name]
    definition = GQLDefinition(
        feature_flags=FeatureFlags(plugin=plugin_name),
        source_file=source_file,
        definition=content,
        fragment_dependencies=[],
        kind=GQLDefinitionType.FRAGMENT,
        name="",
    )
    generated_files = plugin.generate_fragments(definitions=[definition], schema=schema)
    rendered_files: list[GeneratedFile] = expected_files(
        plugin=plugin_name, kind="fragments", definition=fragment
    )
    assert len(rendered_files) == 1

    expected_fragments = [
        Fragment(
            file=rendered_files[0].file,
            content=rendered_files[0].content,
            import_path=import_path,
            class_name=class_name,
            fragment_name=fragment_name,
        )
    ]
    assert generated_files == expected_fragments
