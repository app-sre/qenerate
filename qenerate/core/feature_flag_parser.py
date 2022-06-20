import re
from dataclasses import dataclass


@dataclass
class FeatureFlags:
    plugin: str


class FeatureFlagParser:
    @staticmethod
    def parse(query: str) -> FeatureFlags:
        plugin = ""
        m = re.search(r"# qenerate: plugin\s*=\s*(\w+)\s*", query)
        if m:
            plugin = m.group(1)
        return FeatureFlags(
            plugin=plugin,
        )
