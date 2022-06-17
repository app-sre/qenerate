from pytest import raises

import tests.util as util
from qenerate.core.typed_ast import AnonymousQueryError, InvalidQueryError, TypedAST


def test_anonymous_query():
    ast = TypedAST()

    with raises(AnonymousQueryError):
        ast.build(
            query=util.get_query("anonymous_query.gql"),
            introspection=util.get_introspection(),
        )


def test_invalid_query():
    ast = TypedAST()

    with raises(InvalidQueryError):
        ast.build(
            query=util.get_query("invalid_query.gql"),
            introspection=util.get_introspection(),
        )
