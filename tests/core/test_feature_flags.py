from qenerate.core.feature_flag_parser import FeatureFlags, FeatureFlagParser


def test_feature_flags_plugin():
    content = """
    # qenerate: plugin=PluginV1
    query {}
    """

    flags = FeatureFlagParser.parse(content)
    expected = FeatureFlags(plugin="PluginV1")

    assert flags == expected
