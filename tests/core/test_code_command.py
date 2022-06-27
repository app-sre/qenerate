import os
from typing import Any

from qenerate.core.plugin import Plugin
from qenerate.core.code_command import CodeCommand
from qenerate.core.code_command import plugins


class FakePlugin(Plugin):
    def generate(self, query: str, raw_schema: dict[Any, Any]) -> str:
        return "fake"


def test_single_file(fs):
    fs.add_real_directory("tests/queries")
    fs.create_file(
        "/tmp/my_query.gql",
        contents="# qenerate: plugin=fake",
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
        contents="# qenerate",
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
        contents="# qenerate: plugin=fake",
    )
    fs.create_file(
        "/tmp/sub/my_query.gql",
        contents="# qenerate: plugin=fake",
    )
    fs.create_file(
        "/tmp/sub/my_query2.gql",
        contents="# qenerate: plugin=fake",
    )

    plugins["fake"] = FakePlugin()

    CodeCommand.generate_code(
        introspection_file_path="tests/queries/introspection.json",
        dir="/tmp",
    )

    assert os.path.exists("/tmp/my_query.py")
    assert os.path.exists("/tmp/sub/my_query.py")
    assert os.path.exists("/tmp/sub/my_query2.py")
