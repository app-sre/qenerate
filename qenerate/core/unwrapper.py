from dataclasses import dataclass
from enum import Enum
from graphql import (
    GraphQLEnumType,
    GraphQLOutputType,
    GraphQLNonNull,
    GraphQLList,
    GraphQLScalarType,
)


class WrapperType(Enum):
    LIST = 1
    OPTIONAL = 2


@dataclass
class UnwrapperResult:
    wrapper_stack: list[WrapperType]
    inner_gql_type: GraphQLOutputType
    is_primitive: bool
    enum_map: dict[str, str]


class Unwrapper:
    """
    GraphQLOutputType can be nested in lists and non-optionals.
    Unwrapper is responsible for unwrapping those lists and
    non-optionals.
    """

    @staticmethod
    def unwrap(gql_type: GraphQLOutputType) -> UnwrapperResult:
        wrappers: list[WrapperType] = []
        if isinstance(gql_type, GraphQLNonNull):
            gql_type = gql_type.of_type
        else:
            wrappers.append(WrapperType.OPTIONAL)

        if isinstance(gql_type, GraphQLList):
            res = Unwrapper.unwrap(gql_type.of_type)
            wrappers.append(WrapperType.LIST)
            wrappers.extend(res.wrapper_stack)
            return UnwrapperResult(
                wrapper_stack=wrappers,
                inner_gql_type=res.inner_gql_type,
                is_primitive=res.is_primitive,
                enum_map=res.enum_map,
            )

        enum_map = {}
        if isinstance(gql_type, GraphQLEnumType):
            for k, v in gql_type.values.items():
                enum_map[k] = v.value
        return UnwrapperResult(
            wrapper_stack=wrappers,
            inner_gql_type=gql_type,
            is_primitive=isinstance(gql_type, GraphQLScalarType),
            enum_map=enum_map,
        )
