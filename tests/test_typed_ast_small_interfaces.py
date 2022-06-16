import tests.util as util

from graphql import (
    FieldNode,
    GraphQLInterfaceType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    InlineFragmentNode,
    OperationDefinitionNode,
)

from qenerate.core.typed_ast import TypedAST


def test_build_ast_simple_valid_query():
    ast = TypedAST()
    ast.build(
        query=util.get_query("ocp_with_inline_fragments.gql"),
        introspection=util.get_introspection(),
    )

    assert ast.root != None
    assert ast.root.parent == None

    operation = ast.root.children[0]
    assert isinstance(operation.wrapped, OperationDefinitionNode)
    assert len(operation.children) == 1

    ocp = operation.children[0]
    assert isinstance(ocp.wrapped, FieldNode)
    assert isinstance(ocp.gql_type, GraphQLList)
    assert len(ocp.children) == 1

    hive = ocp.children[0]
    assert isinstance(hive.wrapped, FieldNode)
    assert isinstance(hive.gql_type, GraphQLNonNull)
    assert len(hive.children) == 1

    auth = hive.children[0]
    assert isinstance(auth.wrapped, FieldNode)
    assert isinstance(auth.gql_type, GraphQLInterfaceType)
    assert len(auth.children) == 2

    auth_github_fragment = auth.children[0]
    assert isinstance(auth_github_fragment.wrapped, InlineFragmentNode)
    assert isinstance(auth_github_fragment.gql_type, GraphQLObjectType)
    assert len(auth_github_fragment.children) == 1

    auth_cluster_fragment = auth.children[1]
    assert isinstance(auth_cluster_fragment.wrapped, InlineFragmentNode)
    assert isinstance(auth_cluster_fragment.gql_type, GraphQLObjectType)
    assert len(auth_cluster_fragment.children) == 2

    auth_github_org = auth_github_fragment.children[0]
    assert isinstance(auth_github_org.wrapped, FieldNode)
    assert isinstance(auth_github_org.gql_type, GraphQLNonNull)
    assert len(auth_github_org.children) == 0

    auth_cluster_org = auth_cluster_fragment.children[0]
    assert isinstance(auth_cluster_org.wrapped, FieldNode)
    assert isinstance(auth_cluster_org.gql_type, GraphQLNonNull)
    assert len(auth_cluster_org.children) == 0

    auth_cluster_team = auth_cluster_fragment.children[1]
    assert isinstance(auth_cluster_team.wrapped, FieldNode)
    assert isinstance(auth_cluster_team.gql_type, GraphQLNonNull)
    assert len(auth_cluster_team.children) == 0
