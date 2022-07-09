from dataclasses import dataclass
import json
import os
from typing import Any

from qenerate.core.plugin import Fragment, Plugin
from qenerate.plugins.pydantic_v1.plugin import (
    AnonymousQueryError,
    InvalidQueryError,
    PydanticV1Plugin,
)
from qenerate.core.feature_flag_parser import FeatureFlagError, FeatureFlagParser


plugins: dict[str, Plugin] = {
    "pydantic_v1": PydanticV1Plugin(),
}


@dataclass
class CodeCommandArgs:
    introspection_file_path: str
    queries_dir: str
    fragments_dir: str
    fragments_package_prefix: str


class CodeCommand:
    @staticmethod
    def _find_gql_files(dir: str) -> list[str]:
        result: list[str] = []
        for root, _, files in os.walk(dir):
            for name in files:
                if name.endswith(".gql"):
                    result.append(os.path.join(root, name))
        return result

    @staticmethod
    def generate_fragments(
        dir: str,
        introspection: dict[Any, Any],
        fragments_package_prefix: str,
    ) -> dict[str, Fragment]:
        discovered_fragments: dict[str, Fragment] = {}
        for file in CodeCommand._find_gql_files(dir):
            import_path = fragments_package_prefix
            if import_path and not import_path.endswith("."):
                import_path += "."
            # omit .gql ending of file
            import_path += os.path.relpath(file, dir)[:-4]

            # convert path separators to modules
            import_path = import_path.replace("\\", ".")
            import_path = import_path.replace("/", ".")

            with open(file, "r") as f:
                content = f.read()
                try:
                    feature_flags = FeatureFlagParser.parse(
                        query=content,
                    )
                    if feature_flags.plugin not in plugins:
                        print(
                            f"[Skipping File] Fragment in {file} specifies "
                            "unknown plugin: "
                            f'"# qenerate: plugin={feature_flags.plugin}".'
                        )
                        continue
                    plugin = plugins[feature_flags.plugin]
                    result = plugin.generate_fragment_classes(
                        fragment=content,
                        raw_schema=introspection,
                        import_package=import_path,
                    )
                except FeatureFlagError:
                    print(
                        f"[Skipping File] Fragment in {file} does not "
                        "specify generator plugin via "
                        '"# qenerate: plugin=<plugin_id>" set.'
                    )
                    continue
                with open(f"{file[:-3]}py", "w") as out_file:
                    out_file.write(result.code)
                discovered_fragments = dict(discovered_fragments, **result.fragments)
        return discovered_fragments

    @staticmethod
    def generate_queries(
        dir: str, introspection: dict[Any, Any], fragments: dict[str, Fragment]
    ):
        for file in CodeCommand._find_gql_files(dir):
            with open(file, "r") as f:
                content = f.read()
                try:
                    feature_flags = FeatureFlagParser.parse(
                        query=content,
                    )
                    if feature_flags.plugin not in plugins:
                        print(
                            f"[Skipping File] Query in {file} specifies "
                            "unknown plugin: "
                            f'"# qenerate: plugin={feature_flags.plugin}".'
                        )
                        continue
                    plugin = plugins[feature_flags.plugin]
                    code = plugin.generate_query_classes(
                        query=content,
                        fragments=fragments,
                        raw_schema=introspection,
                    )
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
                with open(f"{file[:-3]}py", "w") as out_file:
                    out_file.write(code)

    @staticmethod
    def generate_code(args: CodeCommandArgs):
        with open(args.introspection_file_path) as f:
            introspection = json.loads(f.read())["data"]

        fragments = CodeCommand.generate_fragments(
            dir=args.fragments_dir,
            introspection=introspection,
            fragments_package_prefix=args.fragments_package_prefix,
        )
        CodeCommand.generate_queries(
            dir=args.queries_dir,
            fragments=fragments,
            introspection=introspection,
        )
