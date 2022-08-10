from dataclasses import dataclass
from typing import Any
from pathlib import Path


@dataclass(eq=True, order=True)
class GeneratedFile:
    file: Path
    content: str

    def __eq__(self, other: object) -> bool:
        # ignore path in filename comparison
        return self.content == self.content and self.file.name == self.file.name

    def save(self):
        self.file.write_text(self.content)


class Plugin:
    def generate(
        self, query_file: str, raw_schema: dict[Any, Any]
    ) -> list[GeneratedFile]:
        raise NotImplementedError


class AnonymousQueryError(Exception):
    def __init__(self):
        super().__init__("All queries must be named")


class InvalidQueryError(Exception):
    def __init__(self, errors):
        self.errors = errors
        message = "\n".join(str(err) for err in errors)
        super().__init__(message)
