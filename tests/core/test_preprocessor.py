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
                    source_file="",  # adjusted in test
                ),
                GQLDefinition(
                    feature_flags=FeatureFlags(plugin="test"),
                    kind=GQLDefinitionType.QUERY,
                    name="SecondQuery",
                    definition="query SecondQuery { other { name } }",
                    source_file="",  # adjusted in test
                ),
            ],
        ],
        # Test a file containing a mutation
        [
            Path("tests/core/preprocessor/queries/mutation.gql"),
            [],
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
