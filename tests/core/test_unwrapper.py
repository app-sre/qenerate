import pytest
from graphql import (
    GraphQLEnumType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLOutputType,
    GraphQLScalarType,
)

from qenerate.core.unwrapper import Unwrapper, UnwrapperResult, WrapperType


@pytest.mark.parametrize(
    ("gql_input", "expected"),
    [
        (
            GraphQLScalarType(name="MyString"),
            UnwrapperResult(
                wrapper_stack=[WrapperType.OPTIONAL],
                inner_gql_type=GraphQLScalarType(name="MyString"),
                is_primitive=True,
                enum_map={},
            ),
        ),
        (
            GraphQLNonNull(GraphQLList(GraphQLObjectType(name="MyObject", fields={}))),
            UnwrapperResult(
                wrapper_stack=[WrapperType.LIST, WrapperType.OPTIONAL],
                inner_gql_type=GraphQLObjectType(name="MyObject", fields={}),
                is_primitive=False,
                enum_map={},
            ),
        ),
        (
            GraphQLList(GraphQLNonNull(GraphQLScalarType(name="Integer"))),
            UnwrapperResult(
                wrapper_stack=[WrapperType.OPTIONAL, WrapperType.LIST],
                inner_gql_type=GraphQLScalarType(name="Integer"),
                is_primitive=True,
                enum_map={},
            ),
        ),
        (
            GraphQLList(GraphQLNonNull(GraphQLList(GraphQLScalarType(name="Integer")))),
            UnwrapperResult(
                wrapper_stack=[
                    WrapperType.OPTIONAL,
                    WrapperType.LIST,
                    WrapperType.LIST,
                    WrapperType.OPTIONAL,
                ],
                inner_gql_type=GraphQLScalarType(name="Integer"),
                is_primitive=True,
                enum_map={},
            ),
        ),
        (
            GraphQLList(
                GraphQLNonNull(
                    GraphQLEnumType(name="Integer", values={"K": "V", "KK": "VV"})
                )
            ),
            UnwrapperResult(
                wrapper_stack=[
                    WrapperType.OPTIONAL,
                    WrapperType.LIST,
                ],
                inner_gql_type=GraphQLEnumType(
                    name="Integer", values={"K": "V", "KK": "VV"}
                ),
                is_primitive=False,
                enum_map={
                    "K": "V",
                    "KK": "VV",
                },
            ),
        ),
    ],
)
def test_unwrapper(gql_input: GraphQLOutputType, expected: UnwrapperResult) -> None:
    result = Unwrapper.unwrap(gql_input)

    assert result.is_primitive == expected.is_primitive
    assert result.wrapper_stack == expected.wrapper_stack
    assert result.inner_gql_type.name == expected.inner_gql_type.name  # type: ignore[union-attr]
