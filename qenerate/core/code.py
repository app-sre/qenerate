import json
import os

from qenerate.core.plugin import Plugin
from qenerate.plugins.pydantic_v1.plugin import (
    AnonymousQueryError,
    InvalidQueryError,
    PydanticV1Plugin,
)


plugins: dict[str, Plugin] = {
    "pydantic_v1": PydanticV1Plugin(),
}


def _find_query_files(dir: str) -> list[str]:
    result: list[str] = []
    for root, _, files in os.walk(dir):
        for name in files:
            if name.endswith(".gql"):
                result.append(os.path.join(root, name))
    return result


def generate_code(introspection_file_path: str, dir: str):
    with open(introspection_file_path) as f:
        introspection = json.loads(f.read())["data"]

    for file in _find_query_files(dir):
        with open(file, "r") as f:
            # TODO: fetch from feature flag
            plugin = plugins["pydantic_v1"]
            try:
                code = plugin.generate(
                    query=f.read(),
                    raw_schema=introspection,
                )
            except AnonymousQueryError:
                print(
                    f"[Skipping File] Query in {file} is anonymous. "
                    "Qenerate does not support anonymous queries."
                    "Please name the query."
                )
                continue
            except InvalidQueryError:
                print("[Skipping File] Schema validation failed for " f"query {file}.")
                continue
            with open(f"{file[:-3]}py", "w") as out_file:
                out_file.write(code)
