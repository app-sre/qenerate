from pathlib import Path
from typing import Iterable
import pytest

from graphql import GraphQLError, GraphQLSyntaxError

from qenerate.core.preprocessor import (
    AnonymousOperationError,
    GQLDefinition,
    GQLDefinitionType,
    Preprocessor,
)
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
                    fragment_dependencies=set(),
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
                    fragment_dependencies=set(),
                    source_file="",  # adjusted in test
                ),
                GQLDefinition(
                    feature_flags=FeatureFlags(plugin="test"),
                    kind=GQLDefinitionType.QUERY,
                    name="SecondQuery",
                    definition="query SecondQuery { other { name } }",
                    fragment_dependencies=set(),
                    source_file="",  # adjusted in test
                ),
            ],
        ],
        # Test a file containing a mutation
        [
            Path("tests/core/preprocessor/queries/mutation.gql"),
            [
                GQLDefinition(
                    feature_flags=FeatureFlags(plugin="test"),
                    kind=GQLDefinitionType.MUTATION,
                    name="CreateReviewForEpisode",
                    definition="mutation CreateReviewForEpisode($ep: Episode!, $review: ReviewInput!) { createReview(episode: $ep, review: $review) { stars commentary } }",
                    fragment_dependencies=set(),
                    source_file="",  # adjusted in test
                ),
            ],
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
                    fragment_dependencies=set(),
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
                    fragment_dependencies=set(),
                    source_file="",  # adjusted in test
                ),
                GQLDefinition(
                    feature_flags=FeatureFlags(plugin="test"),
                    kind=GQLDefinitionType.FRAGMENT,
                    name="My2ndFragment",
                    definition="fragment My2ndFragment on My2ndObject { name }",
                    fragment_dependencies=set(),
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
                    fragment_dependencies=set(["NestedFragment"]),
                    source_file="",  # adjusted in test
                ),
                GQLDefinition(
                    feature_flags=FeatureFlags(plugin="test"),
                    kind=GQLDefinitionType.FRAGMENT,
                    name="NestedFragment",
                    definition="fragment NestedFragment on NestedObject { name }",
                    fragment_dependencies=set(),
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
                    fragment_dependencies=set(["FirstFragment", "SecondFragment"]),
                    source_file="",  # adjusted in test
                ),
                GQLDefinition(
                    feature_flags=FeatureFlags(plugin="test"),
                    kind=GQLDefinitionType.FRAGMENT,
                    name="FirstFragment",
                    definition="fragment FirstFragment on SomeObject { name }",
                    fragment_dependencies=set(),
                    source_file="",  # adjusted in test
                ),
                GQLDefinition(
                    feature_flags=FeatureFlags(plugin="test"),
                    kind=GQLDefinitionType.FRAGMENT,
                    name="SecondFragment",
                    definition="fragment SecondFragment on OtherObject { other { ... NestedFragment } }",
                    fragment_dependencies=set(["NestedFragment"]),
                    source_file="",  # adjusted in test
                ),
                GQLDefinition(
                    feature_flags=FeatureFlags(plugin="test"),
                    kind=GQLDefinitionType.FRAGMENT,
                    name="NestedFragment",
                    definition="fragment NestedFragment on NestedObject { name }",
                    fragment_dependencies=set(),
                    source_file="",  # adjusted in test
                ),
            ],
        ],
        # Test a file containing query having multiple references to same fragment
        [
            Path(
                "tests/core/preprocessor/queries/query_with_multiple_fragment_references.gql"
            ),
            [
                GQLDefinition(
                    feature_flags=FeatureFlags(plugin="test"),
                    kind=GQLDefinitionType.QUERY,
                    name="FirstQuery",
                    definition="query FirstQuery { some { ... MyFragment } other { ... MyFragment } }",
                    fragment_dependencies=set(["MyFragment"]),
                    source_file="",  # adjusted in test
                ),
                GQLDefinition(
                    feature_flags=FeatureFlags(plugin="test"),
                    kind=GQLDefinitionType.FRAGMENT,
                    name="MyFragment",
                    definition="fragment MyFragment on SomeObject { name }",
                    fragment_dependencies=set(),
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


@pytest.mark.parametrize(
    "definitions, raise_error",
    [
        [
            # Bad Syntax
            [
                "{}",
                "blub",
            ],
            GraphQLSyntaxError,
        ],
        [
            # Valid simple query
            [
                "query Test { users_v1 { name } }",
            ],
            None,
        ],
        [
            # Valid query with fragments
            [
                "query Test { users_v1 { ... MyFragment } }",
                "fragment MyFragment on User_v1 { name }",
            ],
            None,
        ],
        [
            # Unused fragment - allow it
            [
                "fragment MyFragment on User_v1 { name }",
            ],
            None,
        ],
        [
            # Unknown fragment
            [
                "query Test { users_v1 { ... MyFragment } }",
            ],
            GraphQLError,
        ],
        [
            # Anonymous query
            [
                "query { users_v1 { name } }",
            ],
            AnonymousOperationError,
        ],
    ],
)
def test_preprocessor_exception(
    app_interface_schema, raise_error, definitions: Iterable[str]
):
    definition_objects = [
        GQLDefinition(
            definition=definition,
            feature_flags=FeatureFlags(plugin="fake"),
            fragment_dependencies=[],
            kind=GQLDefinitionType.QUERY,
            source_file=Path("/tmp"),
            name="",
        )
        for definition in definitions
    ]
    preprocessor = Preprocessor()

    if not raise_error:
        preprocessor.validate(
            definitions=definition_objects, schema=app_interface_schema
        )
        return

    with pytest.raises(raise_error):
        preprocessor.validate(
            definitions=definition_objects, schema=app_interface_schema
        )
