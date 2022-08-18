from pathlib import Path
from typing import Iterable
import pytest

from qenerate.core.preprocessor import GQLDefinition, GQLDefinitionType, Preprocessor
from qenerate.core.feature_flag_parser import FeatureFlags


def normalize_definition(definition: str) -> str:
    return " ".join(definition.split())


@pytest.mark.parametrize(
    "file, expected",
    [
        # Test a file with a single query
        [
            Path("tests/core/preprocessor/queries/single_query.gql"),
            [
                GQLDefinition(
                    feature_flags=FeatureFlags(plugin="test"),
                    kind=GQLDefinitionType.QUERY,
                    name="MyQuery",
                    definition="query MyQuery { some { name } }",
                    fragment_dependencies=[],
                    source_file="",  # adjusted in test
                ),
            ],
        ],
        # Test a file containing multiple queries
        [
            Path("tests/core/preprocessor/queries/multiple_queries.gql"),
            [
                GQLDefinition(
                    feature_flags=FeatureFlags(plugin="test"),
                    kind=GQLDefinitionType.QUERY,
                    name="FirstQuery",
                    definition="query FirstQuery { some { name } }",
                    fragment_dependencies=[],
                    source_file="",  # adjusted in test
                ),
                GQLDefinition(
                    feature_flags=FeatureFlags(plugin="test"),
                    kind=GQLDefinitionType.QUERY,
                    name="SecondQuery",
                    definition="query SecondQuery { other { name } }",
                    fragment_dependencies=[],
                    source_file="",  # adjusted in test
                ),
            ],
        ],
        # Test a file containing a mutation
        [
            Path("tests/core/preprocessor/queries/mutation.gql"),
            [],
        ],
        # Test a file containing a single fragment
        [
            Path("tests/core/preprocessor/fragments/single_fragment.gql"),
            [
                GQLDefinition(
                    feature_flags=FeatureFlags(plugin="test"),
                    kind=GQLDefinitionType.FRAGMENT,
                    name="MyFragment",
                    definition="fragment MyFragment on MyObject { name }",
                    fragment_dependencies=[],
                    source_file="",  # adjusted in test
                ),
            ],
        ],
        # Test a file containing multiple fragments
        [
            Path("tests/core/preprocessor/fragments/multiple_fragments.gql"),
            [
                GQLDefinition(
                    feature_flags=FeatureFlags(plugin="test"),
                    kind=GQLDefinitionType.FRAGMENT,
                    name="MyFragment",
                    definition="fragment MyFragment on MyObject { name }",
                    fragment_dependencies=[],
                    source_file="",  # adjusted in test
                ),
                GQLDefinition(
                    feature_flags=FeatureFlags(plugin="test"),
                    kind=GQLDefinitionType.FRAGMENT,
                    name="My2ndFragment",
                    definition="fragment My2ndFragment on My2ndObject { name }",
                    fragment_dependencies=[],
                    source_file="",  # adjusted in test
                ),
            ],
        ],
        # Test a file containing nested fragments
        [
            Path("tests/core/preprocessor/fragments/nested_fragments.gql"),
            [
                GQLDefinition(
                    feature_flags=FeatureFlags(plugin="test"),
                    kind=GQLDefinitionType.FRAGMENT,
                    name="MyFragment",
                    definition="fragment MyFragment on MyObject { some { ... NestedFragment } }",
                    fragment_dependencies=["NestedFragment"],
                    source_file="",  # adjusted in test
                ),
                GQLDefinition(
                    feature_flags=FeatureFlags(plugin="test"),
                    kind=GQLDefinitionType.FRAGMENT,
                    name="NestedFragment",
                    definition="fragment NestedFragment on NestedObject { name }",
                    fragment_dependencies=[],
                    source_file="",  # adjusted in test
                ),
            ],
        ],
        # Test a file containing query with nested fragments
        [
            Path("tests/core/preprocessor/queries/query_with_fragments.gql"),
            [
                GQLDefinition(
                    feature_flags=FeatureFlags(plugin="test"),
                    kind=GQLDefinitionType.QUERY,
                    name="FirstQuery",
                    definition="query FirstQuery { some { ... FirstFragment } other { ... SecondFragment } }",
                    fragment_dependencies=["FirstFragment", "SecondFragment"],
                    source_file="",  # adjusted in test
                ),
                GQLDefinition(
                    feature_flags=FeatureFlags(plugin="test"),
                    kind=GQLDefinitionType.FRAGMENT,
                    name="FirstFragment",
                    definition="fragment FirstFragment on SomeObject { name }",
                    fragment_dependencies=[],
                    source_file="",  # adjusted in test
                ),
                GQLDefinition(
                    feature_flags=FeatureFlags(plugin="test"),
                    kind=GQLDefinitionType.FRAGMENT,
                    name="SecondFragment",
                    definition="fragment SecondFragment on OtherObject { other { ... NestedFragment } }",
                    fragment_dependencies=["NestedFragment"],
                    source_file="",  # adjusted in test
                ),
                GQLDefinition(
                    feature_flags=FeatureFlags(plugin="test"),
                    kind=GQLDefinitionType.FRAGMENT,
                    name="NestedFragment",
                    definition="fragment NestedFragment on NestedObject { name }",
                    fragment_dependencies=[],
                    source_file="",  # adjusted in test
                ),
            ],
        ],
    ],
)
def test_preprocessor(file: Path, expected: Iterable[GQLDefinition]):
    for ex in expected:
        ex.source_file = file

    preprocessor = Preprocessor()
    definitions = preprocessor.process_file(file)
    for definition in definitions:
        definition.definition = normalize_definition(definition.definition)

    assert definitions == expected
