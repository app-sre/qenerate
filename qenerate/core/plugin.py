from dataclasses import dataclass, field
from pathlib import Path

from graphql import GraphQLSchema

from qenerate.core.preprocessor import GQLDefinition


@dataclass(eq=True, order=True)
class GeneratedFile:
    file: Path = field(compare=False)
    content: str

    def save(self):
        self.file.write_text(self.content)


@dataclass
class Fragment(GeneratedFile):
    definition: GQLDefinition
    import_path: str
    fragment_name: str
    class_name: str


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
