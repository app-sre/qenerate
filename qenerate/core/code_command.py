import json
import os
from pathlib import Path
from typing import cast

from graphql import build_client_schema, IntrospectionQuery

from qenerate.core.plugin import Plugin
from qenerate.core.preprocessor import Preprocessor, GQLDefinition
from qenerate.plugins.pydantic_v1.plugin import (
    AnonymousQueryError,
    InvalidQueryError,
    PydanticV1Plugin,
)
from qenerate.core.feature_flag_parser import FeatureFlagError


plugins: dict[str, Plugin] = {
    "pydantic_v1": PydanticV1Plugin(),
}


class CodeCommand:
    def __init__(
        self, preprocessor: Preprocessor, plugins: dict[str, Plugin] = plugins
    ):
        self._preprocessor = preprocessor
        self._plugins = plugins

    def _find_query_files(self, dir: str) -> list[str]:
        result: list[str] = []
        for root, _, files in os.walk(dir):
            for name in files:
                if name.endswith(".gql"):
                    result.append(os.path.join(root, name))
        return result

    def _preprocess(self, dir: str) -> list[GQLDefinition]:
        definitions: list[GQLDefinition] = []
        for file in self._find_query_files(dir):
            try:
                definitions.extend(self._preprocessor.process_file(Path(file)))
            except FeatureFlagError:
                print(
                    f"[Skipping File] Query in {file} does not "
                    "specify generator plugin via "
                    '"# qenerate: plugin=<plugin_id>" set.'
                )
                continue
            except AnonymousQueryError:
                print(
                    f"[Skipping File] Query in {file} is anonymous. "
                    "Qenerate does not support anonymous queries."
                    "Please name the query."
                )
                continue
            except InvalidQueryError:
                print(f"[Skipping File] Schema validation failed for query {file}.")
                continue
        return definitions

    def generate_code(self, introspection_file_path: str, dir: str):
        with open(introspection_file_path) as f:
            introspection = json.loads(f.read())["data"]

        schema = build_client_schema(cast(IntrospectionQuery, introspection))

        definitions = self._preprocess(dir=dir)
        definitions_by_plugin: dict[str, list[GQLDefinition]] = {
            plugin: [] for plugin in self._plugins.keys()
        }

        for definition in definitions:
            plugin_name = definition.feature_flags.plugin
            if plugin_name not in definitions_by_plugin:
                # TODO: proper logging
                print(
                    f"[WARNING] Unknown plugin: {plugin_name} "
                    f"for {definition.source_file} - Skipping"
                )
                continue
            definitions_by_plugin[definition.feature_flags.plugin].append(definition)

        for plugin, defs in definitions_by_plugin.items():
            generated_files = self._plugins[plugin].generate(
                definitions=defs, schema=schema
            )
            for file in generated_files:
                file.save()
