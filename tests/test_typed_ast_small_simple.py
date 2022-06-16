import tests.util as util

from graphql import FieldNode, GraphQLList, GraphQLNonNull, OperationDefinitionNode

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

    apps_v1 = operation.children[0]
    assert isinstance(apps_v1.wrapped, FieldNode)
    assert isinstance(apps_v1.gql_type, GraphQLList)
    assert len(apps_v1.children) == 1

    saas_files = apps_v1.children[0]
    assert isinstance(saas_files.wrapped, FieldNode)
    assert isinstance(saas_files.gql_type, GraphQLList)
    assert len(saas_files.children) == 2

    saas_file_name = saas_files.children[0]
    assert isinstance(saas_file_name.wrapped, FieldNode)
    assert isinstance(saas_file_name.gql_type, GraphQLNonNull)
    assert len(saas_file_name.children) == 0

    pipeline = saas_files.children[1]
    assert isinstance(pipeline.wrapped, FieldNode)
    assert isinstance(pipeline.gql_type, GraphQLNonNull)
    assert len(pipeline.children) == 1

    pipeline_name = pipeline.children[0]
    assert isinstance(pipeline_name.wrapped, FieldNode)
    assert isinstance(pipeline_name.gql_type, GraphQLNonNull)
    assert len(pipeline_name.children) == 0
