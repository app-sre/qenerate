from dataclasses import dataclass
from typing import Any
from pathlib import Path

from qenerate.core.preprocessor import GQLDefinition


@dataclass(eq=True, order=True)
class GeneratedFile:
    file: Path
    content: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GeneratedFile):
            return False
        # ignore path in filename comparison
        return self.content == other.content and self.file.name == other.file.name

    def save(self):
        self.file.write_text(self.content)


class Plugin:
    def generate(
        self, definition: GQLDefinition, raw_schema: dict[Any, Any]
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
