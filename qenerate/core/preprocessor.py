# ruff: noqa: ANN401
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

from graphql import (
    FragmentDefinitionNode,
    FragmentSpreadNode,
    GraphQLSchema,
    OperationDefinitionNode,
    OperationType,
    Visitor,
    get_operation_ast,
    parse,
    validate,
    visit,
)

from qenerate.core.feature_flag_parser import FeatureFlagParser, FeatureFlags

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path


class AnonymousOperationError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(f"All operations must be named:\n{message}")


class GQLDefinitionType(Enum):
    QUERY = 1
    FRAGMENT = 2
    MUTATION = 3


@dataclass
class GQLDefinition:
    feature_flags: FeatureFlags
    source_file: Path
    kind: GQLDefinitionType
    definition: str
    name: str
    fragment_dependencies: set[str]


class DefinitionVisitor(Visitor):
    def __init__(self, source_file_path: Path, feature_flags: FeatureFlags) -> None:
        Visitor.__init__(self)
        self.definitions: list[GQLDefinition] = []
        self._feature_flags = feature_flags
        self._source_file_path = source_file_path
        self._stack: list[GQLDefinition] = []

    @staticmethod
    def _node_name(
        node: OperationDefinitionNode | FragmentDefinitionNode | FragmentSpreadNode,
    ) -> str:
        if not node.name:
            # TODO: proper error
            raise ValueError(f"{node} does not have a name")
        return node.name.value

    @staticmethod
    def _node_body(
        node: OperationDefinitionNode | FragmentDefinitionNode,
    ) -> str:
        if not node.loc:
            # TODO: proper error
            raise ValueError(f"{node} does not have loc set")
        start = node.loc.start_token.start
        end = node.loc.end_token.end
        return node.loc.source.body[start:end]

    def _add_definition(self) -> None:
        if self._stack:
            self.definitions.append(self._stack.pop())

    def enter_operation_definition(
        self, node: OperationDefinitionNode, *_: Any
    ) -> None:
        body = self._node_body(node)
        name = self._node_name(node)

        if node.operation == OperationType.QUERY:
            definition = GQLDefinition(
                kind=GQLDefinitionType.QUERY,
                definition=body,
                source_file=self._source_file_path,
                feature_flags=self._feature_flags,
                fragment_dependencies=set(),
                name=name,
            )
        elif node.operation == OperationType.MUTATION:
            definition = GQLDefinition(
                kind=GQLDefinitionType.MUTATION,
                definition=body,
                source_file=self._source_file_path,
                feature_flags=self._feature_flags,
                fragment_dependencies=set(),
                name=name,
            )
        else:
            # TODO: logger
            return
        self._stack.append(definition)

    def leave_operation_definition(self, *_: Any) -> None:
        self._add_definition()

    def enter_fragment_spread(self, node: FragmentSpreadNode, *_: Any) -> None:
        self._stack[-1].fragment_dependencies.add(self._node_name(node))

    def enter_fragment_definition(self, node: FragmentDefinitionNode, *_: Any) -> None:
        body = self._node_body(node)
        name = self._node_name(node)

        definition = GQLDefinition(
            kind=GQLDefinitionType.FRAGMENT,
            definition=body,
            source_file=self._source_file_path,
            feature_flags=self._feature_flags,
            fragment_dependencies=set(),
            name=name,
        )
        self._stack.append(definition)

    def leave_fragment_definition(self, *_: Any) -> None:
        self._add_definition()


class Preprocessor:
    @staticmethod
    def validate(definitions: Iterable[GQLDefinition], schema: GraphQLSchema) -> None:
        all_definitions = ""
        for definition in definitions:
            all_definitions += definition.definition + " "
            document_ast = parse(definition.definition)
            operation = get_operation_ast(document_ast)
            if operation and not operation.name:
                raise AnonymousOperationError(message=definition.definition)

        document_ast = parse(all_definitions)

        errors = validate(schema, document_ast)
        for error in errors:
            if "Fragment" in error.message and "is never used" in error.message:
                continue
            raise error

    @staticmethod
    def process_file(file_path: Path) -> list[GQLDefinition]:
        content = file_path.read_text(encoding="utf-8")
        feature_flags = FeatureFlagParser.parse(definition=content)
        document_ast = parse(content)
        visitor = DefinitionVisitor(
            feature_flags=feature_flags,
            source_file_path=file_path,
        )
        visit(document_ast, visitor)
        return visitor.definitions
