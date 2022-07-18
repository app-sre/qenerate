import json
from qenerate.core.plugin import Fragment, Plugin

from qenerate.plugins.pydantic_v1.plugin import PydanticV1Plugin


def fragment_definition(name: str) -> str:
    with open(f"tests/app_sre/gql/fragments/{name}.gql") as f:
        return f.read()


def run_test(name: str, expected_fragments: list[Fragment], plugin: Plugin):
    fragment = fragment_definition(name=name)

    with open(f"tests/app_sre/gql/introspection.json") as f:
        schema = json.loads(f.read())["data"]

    with open(f"tests/app_sre/gql/fragments/expected/pydantic_v1/{name}.py.txt") as f:
        expected_code = f.read()

    result = plugin.generate_fragment_classes(
        fragment=fragment,
        import_package="my.package",
        raw_schema=schema,
    )

    assert result.code == expected_code

    for actual, expected in zip(result.fragments.values(), expected_fragments):
        assert isinstance(actual, Fragment) and isinstance(expected, Fragment)
        assert actual.class_name == expected.class_name
        assert actual.gql_query == expected.gql_query
        assert actual.import_package == expected.import_package


VAULT_ONE = """fragment VaultSecret on VaultSecret_v1 {
    path
    field
    version
    format
}"""

VAULT_TWO = """fragment VaultSecret2 on VaultSecret_v1 {
    path
    field
}"""


def test_single_fragment():
    name = "single_fragment"
    run_test(
        name=name,
        plugin=PydanticV1Plugin(),
        expected_fragments=[
            Fragment(
                class_name="VaultSecret",
                import_package="my.package",
                gql_query=VAULT_ONE,
            ),
        ],
    )


def test_multiple_fragments():
    name = "multiple_fragments"
    run_test(
        name=name,
        plugin=PydanticV1Plugin(),
        expected_fragments=[
            Fragment(
                class_name="VaultSecret",
                import_package="my.package",
                gql_query=VAULT_ONE,
            ),
            Fragment(
                class_name="VaultSecret2",
                import_package="my.package",
                gql_query=VAULT_TWO,
            ),
        ],
    )
