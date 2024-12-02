import json
import os
from pathlib import Path
from typing import cast

from graphql import GraphQLSchema, IntrospectionQuery, build_client_schema

from qenerate.core.feature_flag_parser import FeatureFlagError
from qenerate.core.plugin import GeneratedFile, Plugin
from qenerate.core.preprocessor import GQLDefinition, GQLDefinitionType, Preprocessor
from qenerate.plugins.pydantic_v1.plugin import (
    PydanticV1Plugin,
)

plugins: dict[str, Plugin] = {
    "pydantic_v1": PydanticV1Plugin(),
}


class CodeCommand:
    def __init__(
        self, preprocessor: Preprocessor, plugins: dict[str, Plugin] = plugins
    ) -> None:
        self._preprocessor = preprocessor
        self._plugins = plugins

    @staticmethod
    def _find_query_files(directory: str) -> list[str]:
        result: list[str] = []
        for root, _, files in os.walk(directory):
            result.extend(
                os.path.join(root, name) for name in files if name.endswith(".gql")
            )
        return result

    def _preprocess(self, directory: str, schema: GraphQLSchema) -> list[GQLDefinition]:
        definitions: list[GQLDefinition] = []
        for file in self._find_query_files(directory):
            try:
                definitions.extend(self._preprocessor.process_file(Path(file)))
            except FeatureFlagError:  # noqa: PERF203
                continue
        self._preprocessor.validate(
            definitions=definitions,
            schema=schema,
        )
        return definitions

    def generate_code(self, introspection_file_path: str, directory: str) -> None:
        introspection = json.loads(
            Path(introspection_file_path).read_text(encoding="utf-8")
        )["data"]

        schema = build_client_schema(cast("IntrospectionQuery", introspection))

        definitions = self._preprocess(
            directory=directory,
            schema=schema,
        )
        operations_by_plugin: dict[str, list[GQLDefinition]] = {
            plugin: [] for plugin in self._plugins
        }
        fragments_by_plugin: dict[str, list[GQLDefinition]] = {
            plugin: [] for plugin in self._plugins
        }

        for definition in definitions:
            plugin_name = definition.feature_flags.plugin
            if plugin_name not in self._plugins:
                # TODO: proper logging
                continue

            if definition.kind in {GQLDefinitionType.QUERY, GQLDefinitionType.MUTATION}:
                operations_by_plugin[definition.feature_flags.plugin].append(definition)
            elif definition.kind == GQLDefinitionType.FRAGMENT:
                fragments_by_plugin[definition.feature_flags.plugin].append(definition)

        generated_files: list[GeneratedFile] = []
        for plugin_name in self._plugins:
            plugin = self._plugins[plugin_name]

            rendered_fragments = plugin.generate_fragments(
                definitions=fragments_by_plugin[plugin_name],
                schema=schema,
            )

            rendered_queries = plugin.generate_operations(
                definitions=operations_by_plugin[plugin_name],
                fragments=rendered_fragments,
                schema=schema,
            )

            generated_files.extend(rendered_fragments)
            generated_files.extend(rendered_queries)

        for file in generated_files:
            file.save()
