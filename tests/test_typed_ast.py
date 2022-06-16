import json

from graphql import FieldNode, GraphQLList, GraphQLNonNull, OperationDefinitionNode

from qenerate.typed_ast import ASTNode, TypedAST


def get_query(filename: str) -> str:
    with open(f"tests/queries/{filename}") as f:
        return f.read()


def get_introspection() -> dict:
    with open(f"tests/queries/introspection.json") as f:
        return json.loads(f.read())["data"]


def test_build_ast_simple_valid_query():
    ast = TypedAST()
    ast.build(
        query=get_query("saas_file_simple.gql"),
        introspection=get_introspection(),
    )

    assert ast.root != None
    assert ast.root.parent == None

    operation = ast.root.children[0]
    assert isinstance(operation.wrapped, OperationDefinitionNode)

    apps_v1 = operation.children[0]
    assert isinstance(apps_v1.wrapped, FieldNode)
    assert isinstance(apps_v1.gql_type, GraphQLList)

    saas_files = apps_v1.children[0]
    assert isinstance(saas_files.wrapped, FieldNode)

    saas_file_name = saas_files.children[0]
    assert isinstance(saas_file_name.wrapped, FieldNode)
    assert isinstance(saas_file_name.gql_type, GraphQLNonNull)

    pipeline = saas_files.children[1]
    assert isinstance(pipeline.wrapped, FieldNode)
    assert isinstance(pipeline.gql_type, GraphQLNonNull)

    pipeline_name = pipeline.children[0]
    assert isinstance(pipeline_name.wrapped, FieldNode)
    assert isinstance(pipeline_name.gql_type, GraphQLNonNull)
