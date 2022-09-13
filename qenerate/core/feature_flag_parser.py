from enum import Enum
import re
from dataclasses import dataclass


class NamingCollisionStrategy(Enum):
    PARENT_CONTEXT = 1
    ENUMERATE = 2


@dataclass
class FeatureFlags:
    plugin: str
    collision_strategy: NamingCollisionStrategy = NamingCollisionStrategy.PARENT_CONTEXT


class FeatureFlagError(Exception):
    pass


class FeatureFlagParser:
    @staticmethod
    def plugin(definition: str) -> str:
        m = re.search(r"#\s*qenerate:\s*plugin\s*=\s*(\w+)\s*", definition)
        if not m:
            raise FeatureFlagError(
                "Missing valid qenerate plugin flag in query file: "
                "# qenerate: plugin=<plugin_id>"
            )
        return m.group(1)

    @staticmethod
    def naming_collision_strategy(definition: str) -> NamingCollisionStrategy:
        strategy = NamingCollisionStrategy.PARENT_CONTEXT
        m = re.search(
            r"#\s*qenerate:\s*naming_collision_strategy\s*=\s*(\w+)\s*", definition
        )
        if m:
            try:
                strategy = NamingCollisionStrategy[m.group(1)]
            except KeyError:
                raise FeatureFlagError(
                    f"Unknown naming_collision_strategy: {m.group(1)}"
                )
        return strategy

    @staticmethod
    def parse(definition: str) -> FeatureFlags:
        return FeatureFlags(
            plugin=FeatureFlagParser.plugin(definition=definition),
            collision_strategy=FeatureFlagParser.naming_collision_strategy(
                definition=definition
            ),
        )
