# ruff: noqa: PLR6301,ARG002,S108,PTH110
import os
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from qenerate.core.code_command import CodeCommand
from qenerate.core.feature_flag_parser import FeatureFlags
from qenerate.core.plugin import Fragment, GeneratedFile, Plugin
from qenerate.core.preprocessor import GQLDefinition, GQLDefinitionType, Preprocessor

if TYPE_CHECKING:
    from graphql import GraphQLSchema
    from pyfakefs.fake_filesystem_unittest import FakeFilesystem

SCHEMA_DIR = "tests/generator"
APP_INTERFACE_INTROSPECTION = "introspection-app-interface.json"


class FakePlugin(Plugin):
    def generate_fragments(
        self, definitions: list[GQLDefinition], schema: GraphQLSchema
    ) -> list[Fragment]:
        return []

    def generate_operations(
        self,
        definitions: list[GQLDefinition],
        schema: GraphQLSchema,
        fragments: list[Fragment],
    ) -> list[GeneratedFile]:
        return [
            GeneratedFile(
                file=Path(definition.source_file).with_suffix(".py"), content="fake"
            )
            for definition in definitions
        ]


def fake_preprocessor(files: list[tuple[str, GQLDefinitionType]]) -> Preprocessor:
    side_effect = [
        [
            GQLDefinition(
                feature_flags=FeatureFlags(plugin="fake", gql_scalar_mappings={}),
                definition="",
                fragment_dependencies=set(),
                kind=f[1],
                name="",
                source_file=Path(f[0]),
            ),
        ]
        for f in files
    ]
    preprocessor = MagicMock()
    preprocessor.process_file = MagicMock(
        side_effect=side_effect,
    )
    return preprocessor


def test_single_file(fs: FakeFilesystem) -> None:
    fs.add_real_directory(SCHEMA_DIR)
    fs.create_file(
        "/tmp/my_query.gql",
        contents="",
    )

    code_command = CodeCommand(
        preprocessor=fake_preprocessor(
            files=[("/tmp/my_query.gql", GQLDefinitionType.QUERY)],
        ),
        plugins={"fake": FakePlugin()},
    )
    code_command.generate_code(
        introspection_file_path=f"{SCHEMA_DIR}/{APP_INTERFACE_INTROSPECTION}",
        directory="/tmp",
    )

    assert os.path.exists("/tmp/my_query.py")


def test_unknown_plugin_flag(fs: FakeFilesystem) -> None:
    fs.add_real_directory(SCHEMA_DIR)
    fs.create_file(
        "/tmp/my_query.gql",
        contents="",
    )

    code_command = CodeCommand(
        preprocessor=fake_preprocessor(
            files=[("/tmp/my_query.gql", GQLDefinitionType.QUERY)]
        ),
        plugins={},
    )
    code_command.generate_code(
        introspection_file_path=f"{SCHEMA_DIR}/{APP_INTERFACE_INTROSPECTION}",
        directory="/tmp",
    )

    assert not os.path.exists("/tmp/my_query.py")


def test_dir_tree_with_different_operations(fs: FakeFilesystem) -> None:
    fs.add_real_directory(SCHEMA_DIR)
    fs.create_file(
        "/tmp/my_query.gql",
        contents="",
    )
    fs.create_file(
        "/tmp/sub/my_query.gql",
        contents="",
    )
    fs.create_file(
        "/tmp/sub/my_mutation.gql",
        contents="",
    )

    code_command = CodeCommand(
        preprocessor=fake_preprocessor(
            files=[
                ("/tmp/my_query.gql", GQLDefinitionType.QUERY),
                ("/tmp/sub/my_query.gql", GQLDefinitionType.QUERY),
                ("/tmp/sub/my_mutation.gql", GQLDefinitionType.MUTATION),
            ]
        ),
        plugins={"fake": FakePlugin()},
    )
    code_command.generate_code(
        introspection_file_path=f"{SCHEMA_DIR}/{APP_INTERFACE_INTROSPECTION}",
        directory="/tmp",
    )

    assert os.path.exists("/tmp/my_query.py")
    assert os.path.exists("/tmp/sub/my_query.py")
    assert os.path.exists("/tmp/sub/my_mutation.py")


@pytest.mark.parametrize(
    ("locations", "expected"),
    [
        pytest.param(
            ["FIELD_DEFINITION", "ENUM_VALUE"],
            ["FIELD_DEFINITION", "ENUM_VALUE"],
            id="all-valid",
        ),
        pytest.param(
            ["FIELD_DEFINITION", "NOT_YET_SUPPORTED_LOCATION", "ENUM_VALUE"],
            ["FIELD_DEFINITION", "ENUM_VALUE"],
            id="strips-unsupported",
        ),
        pytest.param(
            ["NOT_YET_SUPPORTED_LOCATION"],
            [],
            id="all-unsupported",
        ),
        pytest.param(
            [],
            [],
            id="empty-locations",
        ),
    ],
)
def test_sanitize_introspection(locations: list[str], expected: list[str]) -> None:
    introspection: dict = {
        "__schema": {
            "directives": [
                {"name": "deprecated", "locations": locations},
            ],
        },
    }
    result = CodeCommand.sanitize_introspection(introspection)
    assert result["__schema"]["directives"][0]["locations"] == expected


def test_sanitize_introspection_no_directives() -> None:
    introspection: dict = {"__schema": {}}
    result = CodeCommand.sanitize_introspection(introspection)
    assert result == {"__schema": {}}
