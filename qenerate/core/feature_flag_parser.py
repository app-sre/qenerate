import re
from dataclasses import dataclass


@dataclass
class FeatureFlags:
    plugin: str


class FeatureFlagError(Exception):
    pass


class FeatureFlagParser:
    @staticmethod
    def parse(query: str) -> FeatureFlags:
        plugin = ""
        m = re.search(r"#\s*qenerate:\s*plugin\s*=\s*(\w+)\s*", query)
        if not m:
            raise FeatureFlagError(
                "Missing valid qenerate plugin flag in query file: "
                "# qenerate: plugin=<plugin_id>"
            )
        plugin = m.group(1)
        return FeatureFlags(
            plugin=plugin,
        )
