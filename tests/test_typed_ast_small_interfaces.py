import tests.util as util

from graphql import (
    FieldNode,
    GraphQLInterfaceType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLScalarType,
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
    assert operation.parent == ast.root

    ocp = operation.children[0]
    assert isinstance(ocp.wrapped, FieldNode)
    assert isinstance(ocp.gql_type, GraphQLList)
    assert isinstance(ocp.gql_type.of_type, GraphQLObjectType)
    assert ocp.gql_type.of_type.name == "OcpReleaseMirror_v1"
    assert len(ocp.children) == 1
    assert ocp.parent == operation

    hive = ocp.children[0]
    assert isinstance(hive.wrapped, FieldNode)
    assert isinstance(hive.gql_type, GraphQLNonNull)
    assert isinstance(hive.gql_type.of_type, GraphQLObjectType)
    assert hive.gql_type.of_type.name == "Cluster_v1"
    assert len(hive.children) == 1
    assert hive.parent == ocp

    auth = hive.children[0]
    assert isinstance(auth.wrapped, FieldNode)
    assert isinstance(auth.gql_type, GraphQLInterfaceType)
    assert auth.gql_type.name == "ClusterAuth_v1"
    assert len(auth.children) == 2
    assert auth.parent == hive

    auth_github_fragment = auth.children[0]
    assert isinstance(auth_github_fragment.wrapped, InlineFragmentNode)
    assert isinstance(auth_github_fragment.gql_type, GraphQLObjectType)
    assert auth_github_fragment.gql_type.name == "ClusterAuthGithubOrg_v1"
    assert len(auth_github_fragment.children) == 1
    assert auth_github_fragment.parent == auth

    auth_cluster_fragment = auth.children[1]
    assert isinstance(auth_cluster_fragment.wrapped, InlineFragmentNode)
    assert isinstance(auth_cluster_fragment.gql_type, GraphQLObjectType)
    assert auth_cluster_fragment.gql_type.name == "ClusterAuthGithubOrgTeam_v1"
    assert len(auth_cluster_fragment.children) == 2
    assert auth_cluster_fragment.parent == auth

    auth_github_org = auth_github_fragment.children[0]
    assert isinstance(auth_github_org.wrapped, FieldNode)
    assert isinstance(auth_github_org.gql_type, GraphQLNonNull)
    assert isinstance(auth_github_org.gql_type.of_type, GraphQLScalarType)
    assert auth_github_org.gql_type.of_type.name == "String"
    assert len(auth_github_org.children) == 0
    assert auth_github_org.parent == auth_github_fragment

    auth_cluster_org = auth_cluster_fragment.children[0]
    assert isinstance(auth_cluster_org.wrapped, FieldNode)
    assert isinstance(auth_cluster_org.gql_type, GraphQLNonNull)
    assert isinstance(auth_cluster_org.gql_type.of_type, GraphQLScalarType)
    assert auth_cluster_org.gql_type.of_type.name == "String"
    assert len(auth_cluster_org.children) == 0
    assert auth_cluster_org.parent == auth_cluster_fragment

    auth_cluster_team = auth_cluster_fragment.children[1]
    assert isinstance(auth_cluster_team.wrapped, FieldNode)
    assert isinstance(auth_cluster_team.gql_type, GraphQLNonNull)
    assert isinstance(auth_cluster_team.gql_type.of_type, GraphQLScalarType)
    assert auth_cluster_team.gql_type.of_type.name == "String"
    assert len(auth_cluster_team.children) == 0
    assert auth_cluster_team.parent == auth_cluster_fragment
