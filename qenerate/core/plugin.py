from typing import Any


class Plugin:
    def generate(self, query_file: str, raw_schema: dict[Any, Any]) -> str:
        raise NotImplementedError
