import os
from pathlib import Path
from typing import Any

from qenerate.core.plugin import Plugin, GeneratedFile
from qenerate.core.code_command import CodeCommand
from qenerate.core.code_command import plugins
from qenerate.core.preprocessor import GQLDefinition


class FakePlugin(Plugin):
    def generate(
        self, definition: GQLDefinition, raw_schema: dict[Any, Any]
    ) -> list[GeneratedFile]:
        return [
            GeneratedFile(
                file=Path(definition.source_file).with_suffix(".py"), content="fake"
            )
        ]


def test_single_file(fs):
    fs.add_real_directory("tests/queries")
    fs.create_file(
        "/tmp/my_query.gql",
        contents="""
        # qenerate: plugin=fake
        query MyQuery { some }
        """,
    )

    plugins["fake"] = FakePlugin()

    CodeCommand.generate_code(
        introspection_file_path="tests/queries/introspection.json",
        dir="/tmp",
    )

    assert os.path.exists("/tmp/my_query.py")


def test_single_file_no_plugin_flag(fs):
    fs.add_real_directory("tests/queries")
    fs.create_file(
        "/tmp/my_query.gql",
        contents="""
        # qenerate
        query MyQuery { some }
        """,
    )

    plugins["fake"] = FakePlugin()

    CodeCommand.generate_code(
        introspection_file_path="tests/queries/introspection.json",
        dir="/tmp",
    )

    assert not os.path.exists("/tmp/my_query.py")


def test_unknown_plugin_flag(fs):
    fs.add_real_directory("tests/queries")
    fs.create_file(
        "/tmp/my_query.gql",
        contents="""
        # qenerate: plugin=does_not_exist
        query MyQuery { some }
        """,
    )

    plugins["fake"] = FakePlugin()

    CodeCommand.generate_code(
        introspection_file_path="tests/queries/introspection.json",
        dir="/tmp",
    )

    assert not os.path.exists("/tmp/my_query.py")


def test_dir_tree(fs):
    fs.add_real_directory("tests/queries")
    fs.create_file(
        "/tmp/my_query.gql",
        contents="""
        # qenerate: plugin=fake
        query MyQuery { some }
        """,
    )
    fs.create_file(
        "/tmp/sub/my_query.gql",
        contents="""
        # qenerate: plugin=fake
        query MyQuery { some }
        """,
    )
    fs.create_file(
        "/tmp/sub/my_query2.gql",
        contents="""
        # qenerate: plugin=fake
        query MyQuery { some }
        """,
    )

    plugins["fake"] = FakePlugin()

    CodeCommand.generate_code(
        introspection_file_path="tests/queries/introspection.json",
        dir="/tmp",
    )

    assert os.path.exists("/tmp/my_query.py")
    assert os.path.exists("/tmp/sub/my_query.py")
    assert os.path.exists("/tmp/sub/my_query2.py")
