import json
import os
from pathlib import Path
from typing import cast

from graphql import build_client_schema, IntrospectionQuery, GraphQLSchema

from qenerate.core.plugin import GeneratedFile, Plugin
from qenerate.core.preprocessor import GQLDefinitionType, Preprocessor, GQLDefinition
from qenerate.plugins.pydantic_v1.plugin import (
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

    def _preprocess(self, dir: str, schema: GraphQLSchema) -> list[GQLDefinition]:
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
        self._preprocessor.validate(
            definitions=definitions,
            schema=schema,
        )
        return definitions

    def generate_code(self, introspection_file_path: str, dir: str):
        with open(introspection_file_path) as f:
            introspection = json.loads(f.read())["data"]

        schema = build_client_schema(cast(IntrospectionQuery, introspection))

        definitions = self._preprocess(
            dir=dir,
            schema=schema,
        )
        queries_by_plugin: dict[str, list[GQLDefinition]] = {
            plugin: [] for plugin in self._plugins.keys()
        }
        fragments_by_plugin: dict[str, list[GQLDefinition]] = {
            plugin: [] for plugin in self._plugins.keys()
        }

        for definition in definitions:
            plugin_name = definition.feature_flags.plugin
            if plugin_name not in self._plugins.keys():
                # TODO: proper logging
                print(
                    f"[WARNING] Unknown plugin: {plugin_name} "
                    f"for {definition.source_file} - Skipping"
                )
                continue

            if definition.kind == GQLDefinitionType.QUERY:
                queries_by_plugin[definition.feature_flags.plugin].append(definition)
            elif definition.kind == GQLDefinitionType.FRAGMENT:
                fragments_by_plugin[definition.feature_flags.plugin].append(definition)

        generated_files: list[GeneratedFile] = []
        for plugin_name in self._plugins.keys():
            plugin = self._plugins[plugin_name]

            rendered_fragments = plugin.generate_fragments(
                definitions=fragments_by_plugin[plugin_name],
                schema=schema,
            )

            rendered_queries = plugin.generate_queries(
                definitions=queries_by_plugin[plugin_name],
                fragments=rendered_fragments,
                schema=schema,
            )

            generated_files.extend(rendered_fragments)
            generated_files.extend(rendered_queries)

        for file in generated_files:
            file.save()
