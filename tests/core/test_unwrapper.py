import pytest

from qenerate.core.unwrapper import Unwrapper, UnwrapperResult, WrapperType

from graphql import (
    GraphQLOutputType,
    GraphQLScalarType,
    GraphQLNonNull,
    GraphQLList,
    GraphQLObjectType,
)


@pytest.mark.parametrize(
    "input, expected",
    [
        [
            GraphQLScalarType(name="String"),
            UnwrapperResult(
                wrapper_stack=[WrapperType.OPTIONAL],
                inner_gql_type=GraphQLScalarType(name="String"),
                is_primitive=True,
            ),
        ],
        [
            GraphQLNonNull(GraphQLList(GraphQLObjectType(name="MyObject", fields=[]))),
            UnwrapperResult(
                wrapper_stack=[WrapperType.LIST, WrapperType.OPTIONAL],
                inner_gql_type=GraphQLObjectType(name="MyObject", fields=[]),
                is_primitive=False,
            ),
        ],
        [
            GraphQLList(GraphQLNonNull(GraphQLScalarType(name="Integer"))),
            UnwrapperResult(
                wrapper_stack=[WrapperType.OPTIONAL, WrapperType.LIST],
                inner_gql_type=GraphQLScalarType(name="Integer"),
                is_primitive=True,
            ),
        ],
        [
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
            ),
        ],
    ],
)
def test_unwrapper(input: GraphQLOutputType, expected: UnwrapperResult):
    result = Unwrapper.unwrap(input)

    assert result.is_primitive == expected.is_primitive
    assert result.wrapper_stack == expected.wrapper_stack
    assert result.inner_gql_type.name == expected.inner_gql_type.name
