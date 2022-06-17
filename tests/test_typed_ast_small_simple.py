import tests.util as util

from graphql import (
    FieldNode,
    GraphQLInterfaceType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLScalarType,
    OperationDefinitionNode,
)

from qenerate.core.typed_ast import TypedAST


def test_build_ast_simple_valid_query():
    ast = TypedAST()
    ast.build(
        query=util.get_query("saas_file_simple.gql"),
        introspection=util.get_introspection(),
    )

    assert ast.root != None
    assert ast.root.parent == None

    operation = ast.root.children[0]
    assert isinstance(operation.wrapped, OperationDefinitionNode)
    assert len(operation.children) == 1
    assert operation.parent == ast.root

    apps_v1 = operation.children[0]
    assert isinstance(apps_v1.wrapped, FieldNode)
    assert isinstance(apps_v1.gql_type, GraphQLList)
    assert isinstance(apps_v1.gql_type.of_type, GraphQLObjectType)
    assert len(apps_v1.children) == 1
    assert apps_v1.parent == operation

    saas_files = apps_v1.children[0]
    assert isinstance(saas_files.wrapped, FieldNode)
    assert isinstance(saas_files.gql_type, GraphQLList)
    assert isinstance(saas_files.gql_type.of_type, GraphQLObjectType)
    assert saas_files.gql_type.of_type.name == "SaasFile_v2"
    assert len(saas_files.children) == 2
    assert saas_files.parent == apps_v1

    saas_file_name = saas_files.children[0]
    assert isinstance(saas_file_name.wrapped, FieldNode)
    assert isinstance(saas_file_name.gql_type, GraphQLNonNull)
    assert isinstance(saas_file_name.gql_type.of_type, GraphQLScalarType)
    assert saas_file_name.gql_type.of_type.name == "String"
    assert len(saas_file_name.children) == 0
    assert saas_file_name.parent == saas_files

    pipeline = saas_files.children[1]
    assert isinstance(pipeline.wrapped, FieldNode)
    assert isinstance(pipeline.gql_type, GraphQLNonNull)
    assert isinstance(pipeline.gql_type.of_type, GraphQLInterfaceType)
    assert pipeline.gql_type.of_type.name == "PipelinesProvider_v1"
    assert len(pipeline.children) == 1
    assert pipeline.parent == saas_files

    pipeline_name = pipeline.children[0]
    assert isinstance(pipeline_name.wrapped, FieldNode)
    assert isinstance(pipeline_name.gql_type, GraphQLNonNull)
    assert isinstance(pipeline_name.gql_type.of_type, GraphQLScalarType)
    assert pipeline_name.gql_type.of_type.name == "String"
    assert len(pipeline_name.children) == 0
    assert pipeline_name.parent == pipeline
