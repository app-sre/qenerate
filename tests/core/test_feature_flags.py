import pytest
from qenerate.core.feature_flag_parser import (
    FeatureFlagError,
    FeatureFlags,
    FeatureFlagParser,
)


def test_feature_flags_plugin():
    content = """
    # qenerate: plugin=PluginV1
    query {}
    """

    flags = FeatureFlagParser.parse(
        query=content,
    )
    expected = FeatureFlags(plugin="PluginV1")

    assert flags == expected


def test_feature_flags_plugin_missing():
    content = """
    query {}
    """

    with pytest.raises(FeatureFlagError) as f:
        FeatureFlagParser.parse(
            query=content,
        )

    assert str(f.value) == (
        "Missing valid qenerate plugin flag in query file: "
        "# qenerate: plugin=<plugin_id>"
    )
