import json
from qenerate.core.plugin import Plugin

from qenerate.plugins.pydantic_v1.plugin import PydanticV1Plugin


def run_test(name: str, plugin: Plugin):
    with open(f"tests/app_sre/gql/single_valid_queries/{name}.gql") as f:
        query = f.read()

    with open(f"tests/app_sre/gql/introspection.json") as f:
        schema = json.loads(f.read())["data"]

    with open(
        f"tests/app_sre/gql/single_valid_queries/expected/pydantic_v1/{name}.py.txt"
    ) as f:
        expected = f.read()

    result = plugin.generate_query_classes(
        query=query,
        fragments={},
        raw_schema=schema,
    )

    assert result == expected


def test_complex_inline_fragments_and_collisions():
    name = "complex_inline_fragments_and_collisions"
    run_test(
        name=name,
        plugin=PydanticV1Plugin(),
    )


def test_difficult_attribute_name():
    name = "difficult_attribute_name"
    run_test(
        name=name,
        plugin=PydanticV1Plugin(),
    )


def test_ocp_with_inline_fragments():
    name = "ocp_with_inline_fragments"
    run_test(
        name=name,
        plugin=PydanticV1Plugin(),
    )


def test_saas_file_json():
    name = "saas_file_json"
    run_test(
        name=name,
        plugin=PydanticV1Plugin(),
    )


def test_saas_file_simple():
    name = "saas_file_simple"
    run_test(
        name=name,
        plugin=PydanticV1Plugin(),
    )


def test_saas_humongous():
    name = "saas_humongous"
    run_test(
        name=name,
        plugin=PydanticV1Plugin(),
    )
