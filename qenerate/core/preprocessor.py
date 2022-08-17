from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from graphql import parse, visit, Visitor, OperationDefinitionNode, OperationType

from qenerate.core.feature_flag_parser import FeatureFlagParser, FeatureFlags


class GQLDefinitionType(Enum):
    QUERY = 1


@dataclass
class GQLDefinition:
    feature_flags: FeatureFlags
    source_file: Path
    kind: GQLDefinitionType
    definition: str
    name: str


class DefinitionVisitor(Visitor):
    def __init__(self, source_file_path: Path, feature_flags: FeatureFlags):
        Visitor.__init__(self)
        self.definitions: list[GQLDefinition] = []
        self._feature_flags = feature_flags
        self._source_file_path = source_file_path
        self._current: Optional[GQLDefinition] = None

    def enter_operation_definition(self, node: OperationDefinitionNode, *_):
        if not node.loc:
            # TODO: proper error
            raise ValueError(f"{node} does not have loc set")

        if not node.name:
            # TODO: proper error
            raise ValueError(f"{node} does not have a name")
        start = node.loc.start_token.start
        end = node.loc.end_token.end
        body = node.loc.source.body[start:end]

        if node.operation != OperationType.QUERY:
            # TODO: logger
            # TODO: raise
            print(
                "[WARNING] Skipping operation definition because"
                f" it is not a query: \n{body}"
            )
            return

        definition = GQLDefinition(
            kind=GQLDefinitionType.QUERY,
            definition=body,
            source_file=self._source_file_path,
            feature_flags=self._feature_flags,
            name=node.name.value,
        )
        self._current = definition

    def leave_operation_definition(self, *_):
        if self._current:
            self.definitions.append(self._current)
        self._current = None


class Preprocessor:
    def process_file(self, file_path: Path) -> list[GQLDefinition]:
        with open(file_path, "r") as f:
            content = f.read()
        feature_flags = FeatureFlagParser.parse(
            query=content,
        )
        document_ast = parse(content)
        visitor = DefinitionVisitor(
            feature_flags=feature_flags,
            source_file_path=file_path,
        )
        visit(document_ast, visitor)
        return visitor.definitions
