import json
from qenerate.core.plugin import Fragment, Plugin

from qenerate.plugins.pydantic_v1.plugin import PydanticV1Plugin


def get_gql_file(name: str) -> str:
    with open(f"tests/app_sre/gql/query_with_flat_fragments/{name}.gql") as f:
        return f.read()


def get_expected(name: str) -> str:
    with open(
        f"tests/app_sre/gql/query_with_flat_fragments/expected/pydantic_v1/{name}.py.txt"
    ) as f:
        return f.read()


def run_test(fragment_name: str, query_name: str):
    with open(f"tests/app_sre/gql/introspection.json") as f:
        schema = json.loads(f.read())["data"]

    fragment_definition = get_gql_file(fragment_name)
    query_definition = get_gql_file(query_name)
    plugin = PydanticV1Plugin()
    fragments_result = plugin.generate_fragment_classes(
        raw_schema=schema,
        fragment=fragment_definition,
        import_package="my.package",
    )

    assert fragments_result.code == get_expected(fragment_name)

    query_result = plugin.generate_query_classes(
        raw_schema=schema,
        query=query_definition,
        fragments=fragments_result.fragments,
    )

    assert query_result == get_expected(query_name)


def test_simple_query_with_flat_fragments():
    run_test(
        fragment_name="fragments",
        query_name="simple_query",
    )


def test_interface_query_with_flat_fragments():
    run_test(
        fragment_name="fragments",
        query_name="interface_query",
    )


def test_interface_inline_fragments_query_with_flat_fragments():
    run_test(
        fragment_name="fragments",
        query_name="interface_inline_fragments_query",
    )


def test_partial_inline_fragments_query_with_flat_fragments():
    run_test(
        fragment_name="fragments",
        query_name="partial_inline_fragments_query",
    )


def test_complex_inline_fragments_query_with_flat_fragments():
    run_test(
        fragment_name="fragments",
        query_name="complex_inline_fragments_query",
    )
