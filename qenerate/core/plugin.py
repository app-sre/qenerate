from dataclasses import dataclass
from pathlib import Path

from graphql import GraphQLSchema

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


@dataclass
class Fragment(GeneratedFile):
    definition: GQLDefinition
    import_path: str
    fragment_name: str
    class_name: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Fragment):
            return False
        # ignore path in filename comparison
        return (
            self.content == other.content
            and self.file.name == other.file.name
            and self.class_name == other.class_name
            and self.fragment_name == other.fragment_name
            and self.import_path == other.import_path
        )


class Plugin:
    def generate_queries(
        self,
        definitions: list[GQLDefinition],
        schema: GraphQLSchema,
        fragments: list[Fragment],
    ) -> list[GeneratedFile]:
        raise NotImplementedError

    def generate_fragments(
        self, definitions: list[GQLDefinition], schema: GraphQLSchema
    ) -> list[Fragment]:
        raise NotImplementedError
