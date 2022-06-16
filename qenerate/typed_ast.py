from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Union, Any, cast

from graphql import (
    GraphQLSchema,
    InlineFragmentNode,
    IntrospectionQuery,
    OperationDefinitionNode,
    TypeInfo,
    Visitor,
    TypeInfoVisitor,
    FieldNode,
    visit,
    parse,
    get_operation_ast,
    validate,
    build_client_schema,
    GraphQLScalarType,
    GraphQLObjectType,
    GraphQLInterfaceType,
    GraphQLUnionType,
    GraphQLEnumType,
    GraphQLWrappingType,
)


GQLType = Union[
    GraphQLScalarType,
    GraphQLObjectType,
    GraphQLInterfaceType,
    GraphQLUnionType,
    GraphQLEnumType,
    GraphQLWrappingType[Any],
]


@dataclass
class ASTNode:
    children: list[ASTNode]
    parent: Optional[ASTNode]


@dataclass
class TypedASTNode(ASTNode):
    wrapped: Union[InlineFragmentNode, OperationDefinitionNode, FieldNode]
    gql_type: Optional[GQLType]


class AnonymousQueryError(Exception):
    def __init__(self):
        super().__init__("All queries must be named")


class InvalidQueryError(Exception):
    def __init__(self, errors):
        self.errors = errors
        message = "\n".join(str(err) for err in errors)
        super().__init__(message)


class FieldToTypeMatcherVisitor(Visitor):
    def __init__(self, schema: GraphQLSchema, type_info: TypeInfo, query: str):
        # These are required for GQL Visitor to do its magic
        Visitor.__init__(self)
        self.schema = schema
        self.type_info = type_info
        self.query = query

        # These are our custom fields
        self.parsed = ASTNode(
            children=[],
            parent=None,
        )
        self.parent = self.parsed

    # GQL core lib visitor functions
    def enter_inline_fragment(self, node: InlineFragmentNode, *_):
        graphql_type = self.type_info.get_type()
        current = TypedASTNode(
            children=[],
            parent=self.parent,
            wrapped=node,
            gql_type=graphql_type,
        )
        self.parent.children.append(current)
        self.parent = current

    def leave_inline_fragment(self, *_):
        self.parent = self.parent.parent if self.parent else self.parent

    def enter_operation_definition(self, node: OperationDefinitionNode, *_):
        graphql_type = self.type_info.get_type()
        current = TypedASTNode(
            parent=self.parent,
            children=[],
            wrapped=node,
            gql_type=graphql_type,
        )
        self.parent.children.append(current)
        self.parent = current

    def leave_operation_definition(self, *_):
        self.parent = self.parent.parent if self.parent else self.parent

    def enter_field(self, node: FieldNode, *_):
        graphql_type = self.type_info.get_type()
        current = TypedASTNode(
            children=[],
            parent=self.parent,
            wrapped=node,
            gql_type=graphql_type,
        )

        self.parent.children.append(current)
        self.parent = current

    def leave_field(self, *_):
        self.parent = self.parent.parent if self.parent else self.parent


class TypedAST:
    def __init__(self):
        self.root: ASTNode = None

    def build(self, query: str, introspection: dict):
        schema = build_client_schema(cast(IntrospectionQuery, introspection))
        document_ast = parse(query)
        operation = get_operation_ast(document_ast)

        if operation and not operation.name:
            raise AnonymousQueryError()

        errors = validate(schema, document_ast)
        if errors:
            raise InvalidQueryError(errors)

        type_info = TypeInfo(schema)
        visitor = FieldToTypeMatcherVisitor(schema, type_info, query)
        visit(document_ast, TypeInfoVisitor(type_info, visitor))
        self.root = visitor.parsed
