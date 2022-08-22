import os
from pathlib import Path
from unittest.mock import MagicMock

from graphql import GraphQLSchema
from qenerate.core.feature_flag_parser import FeatureFlags

from qenerate.core.plugin import Fragment, Plugin, GeneratedFile
from qenerate.core.code_command import CodeCommand
from qenerate.core.preprocessor import GQLDefinition, GQLDefinitionType, Preprocessor


class FakePlugin(Plugin):
    def generate_fragments(
        self, definitions: list[GQLDefinition], schema: GraphQLSchema
    ) -> list[Fragment]:
        return []

    def generate_queries(
        self,
        definitions: list[GQLDefinition],
        fragments: list[Fragment],
        schema: GraphQLSchema,
    ) -> list[GeneratedFile]:
        return [
            GeneratedFile(
                file=Path(definition.source_file).with_suffix(".py"), content="fake"
            )
            for definition in definitions
        ]


def fake_preprocessor(files: list[str]) -> Preprocessor:
    side_effect = [
        [
            GQLDefinition(
                feature_flags=FeatureFlags(plugin="fake"),
                definition="",
                fragment_dependencies=[],
                kind=GQLDefinitionType.QUERY,
                name="",
                source_file=Path(f),
            )
        ]
        for f in files
    ]
    preprocessor = MagicMock()
    preprocessor.process_file = MagicMock(
        side_effect=side_effect,
    )
    return preprocessor


def test_single_file(fs):
    fs.add_real_directory("tests/queries")
    fs.create_file(
        "/tmp/my_query.gql",
        contents="",
    )

    code_command = CodeCommand(
        preprocessor=fake_preprocessor(
            files=["/tmp/my_query.gql"],
        ),
        plugins={"fake": FakePlugin()},
    )
    code_command.generate_code(
        introspection_file_path="tests/queries/introspection.json",
        dir="/tmp",
    )

    assert os.path.exists("/tmp/my_query.py")


def test_unknown_plugin_flag(fs):
    fs.add_real_directory("tests/queries")
    fs.create_file(
        "/tmp/my_query.gql",
        contents="",
    )

    code_command = CodeCommand(
        preprocessor=fake_preprocessor(files=["/tmp/my_query.gql"]),
        plugins={},
    )
    code_command.generate_code(
        introspection_file_path="tests/queries/introspection.json",
        dir="/tmp",
    )

    assert not os.path.exists("/tmp/my_query.py")


def test_dir_tree(fs):
    fs.add_real_directory("tests/queries")
    fs.create_file(
        "/tmp/my_query.gql",
        contents="",
    )
    fs.create_file(
        "/tmp/sub/my_query.gql",
        contents="",
    )
    fs.create_file(
        "/tmp/sub/my_query2.gql",
        contents="",
    )

    code_command = CodeCommand(
        preprocessor=fake_preprocessor(
            files=[
                "/tmp/my_query.gql",
                "/tmp/sub/my_query.gql",
                "/tmp/sub/my_query2.gql",
            ]
        ),
        plugins={"fake": FakePlugin()},
    )
    code_command.generate_code(
        introspection_file_path="tests/queries/introspection.json",
        dir="/tmp",
    )

    assert os.path.exists("/tmp/my_query.py")
    assert os.path.exists("/tmp/sub/my_query.py")
    assert os.path.exists("/tmp/sub/my_query2.py")
