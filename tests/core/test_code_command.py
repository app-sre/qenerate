import os
from typing import Any, Mapping

from qenerate.core.plugin import Fragment, Plugin
from qenerate.core.code_command import CodeCommand, CodeCommandArgs
from qenerate.core.code_command import plugins


class FakePlugin(Plugin):
    def generate_query_classes(
        self,
        query: str,
        fragments: Mapping[str, Fragment],
        raw_schema: Mapping[Any, Any],
    ) -> str:
        return "fake"

    def generate_fragment_classes(
        self, fragment: str, raw_schema: dict[Any, Any]
    ) -> str:
        return "fake_fragment"


def add_introspection(fs):
    fs.add_real_directory("tests/app_sre/gql")


INTROSPECTION = "tests/app_sre/gql/introspection.json"


def test_single_file(fs):
    add_introspection(fs)
    fs.create_file(
        "/tmp/my_query.gql",
        contents="# qenerate: plugin=fake",
    )

    plugins["fake"] = FakePlugin()

    CodeCommand.generate_code(
        CodeCommandArgs(
            introspection_file_path=INTROSPECTION,
            fragments_dir="/no",
            queries_dir="/tmp",
            fragments_package_prefix="",
        )
    )

    assert os.path.exists("/tmp/my_query.py")


def test_single_file_no_plugin_flag(fs):
    add_introspection(fs)
    fs.create_file(
        "/tmp/my_query.gql",
        contents="# qenerate",
    )

    plugins["fake"] = FakePlugin()

    CodeCommand.generate_code(
        CodeCommandArgs(
            introspection_file_path=INTROSPECTION,
            fragments_dir="/no",
            queries_dir="/tmp",
            fragments_package_prefix="",
        )
    )

    assert not os.path.exists("/tmp/my_query.py")


def test_unknown_plugin_flag(fs):
    add_introspection(fs)
    fs.create_file(
        "/tmp/my_query.gql",
        contents="# qenerate: plugin=does_not_exist",
    )

    plugins["fake"] = FakePlugin()

    CodeCommand.generate_code(
        CodeCommandArgs(
            introspection_file_path=INTROSPECTION,
            fragments_dir="/no",
            queries_dir="/tmp",
            fragments_package_prefix="",
        )
    )

    assert not os.path.exists("/tmp/my_query.py")


def test_dir_tree(fs):
    add_introspection(fs)
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
        CodeCommandArgs(
            introspection_file_path=INTROSPECTION,
            fragments_dir="/no",
            queries_dir="/tmp",
            fragments_package_prefix="",
        )
    )

    assert os.path.exists("/tmp/my_query.py")
    assert os.path.exists("/tmp/sub/my_query.py")
    assert os.path.exists("/tmp/sub/my_query2.py")
