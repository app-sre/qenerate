import pytest

from qenerate.core.feature_flag_parser import (
    FeatureFlagError,
    FeatureFlagParser,
    FeatureFlags,
    NamingCollisionStrategy,
)


@pytest.mark.parametrize(
    "definition, expected_flags",
    [
        [
            """
            # qenerate: plugin=PluginV1
            query {}
            """,
            FeatureFlags(
                plugin="PluginV1",
                collision_strategy=NamingCollisionStrategy.PARENT_CONTEXT,
                gql_scalar_mappings={},
            ),
        ],
        [
            """
            # qenerate: plugin=PluginV1
            # qenerate: naming_collision_strategy=ENUMERATE
            query {}
            """,
            FeatureFlags(
                plugin="PluginV1",
                collision_strategy=NamingCollisionStrategy.ENUMERATE,
                gql_scalar_mappings={},
            ),
        ],
        [
            """
            # qenerate: plugin=PluginV1
            # qenerate: naming_collision_strategy=PARENT_CONTEXT
            query {}
            """,
            FeatureFlags(
                plugin="PluginV1",
                collision_strategy=NamingCollisionStrategy.PARENT_CONTEXT,
                gql_scalar_mappings={},
            ),
        ],
        [
            """
            # qenerate: plugin=PluginV1
            # qenerate: map_gql_scalar=JSON -> str
            query {}
            """,
            FeatureFlags(
                plugin="PluginV1",
                collision_strategy=NamingCollisionStrategy.PARENT_CONTEXT,
                gql_scalar_mappings={"JSON": "str"},
            ),
        ],
        [
            """
            # qenerate: plugin=PluginV1
            # qenerate: map_gql_scalar=JSON -> str
            # qenerate: map_gql_scalar=A -> B
            query {}
            """,
            FeatureFlags(
                plugin="PluginV1",
                collision_strategy=NamingCollisionStrategy.PARENT_CONTEXT,
                gql_scalar_mappings={"JSON": "str", "A": "B"},
            ),
        ],
    ],
)
def test_valid_feature_flags(definition: str, expected_flags: FeatureFlags):
    flags = FeatureFlagParser.parse(
        definition=definition,
    )

    assert flags == expected_flags


@pytest.mark.parametrize(
    "definition, expected_message",
    [
        [
            """
            query {}
            """,
            (
                "Missing valid qenerate plugin flag in query file: "
                "# qenerate: plugin=<plugin_id>"
            ),
        ],
        [
            """
            # qenerate: plugin=PluginV1
            # qenerate: naming_collision_strategy=DOES_NOT_EXIST
            query {}
            """,
            ("Unknown naming_collision_strategy: DOES_NOT_EXIST"),
        ],
    ],
)
def test_feature_flags_exceptions(definition: str, expected_message: str):
    with pytest.raises(FeatureFlagError) as f:
        FeatureFlagParser.parse(
            definition=definition,
        )

    assert str(f.value) == expected_message
