# ruff: noqa: ANN401
from __future__ import annotations

import operator
from functools import reduce
from typing import TYPE_CHECKING, Any

from graphql import (
    FieldNode,
    FragmentDefinitionNode,
    FragmentSpreadNode,
    GraphQLOutputType,
    GraphQLScalarType,
    GraphQLSchema,
    InlineFragmentNode,
    OperationDefinitionNode,
    TypeInfo,
    TypeInfoVisitor,
    Visitor,
    parse,
    visit,
)

from qenerate.core.feature_flag_parser import FeatureFlags, NamingCollisionStrategy
from qenerate.core.plugin import (
    Fragment,
    GeneratedFile,
    Plugin,
)
from qenerate.core.preprocessor import GQLDefinition, GQLDefinitionType
from qenerate.core.unwrapper import Unwrapper, WrapperType
from qenerate.plugins.pydantic.mapper import (
    graphql_class_name_str_to_python,
    graphql_class_name_to_python,
    graphql_field_name_to_python,
    graphql_primitive_to_python,
)
from qenerate.plugins.pydantic.typed_ast import (
    BASE_CLASS_NAME,
    ParsedClassNode,
    ParsedFieldType,
    ParsedFragmentDefinitionNode,
    ParsedFragmentSpreadNode,
    ParsedInlineFragmentNode,
    ParsedNode,
    ParsedOperationNode,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

INDENT = "    "


def query_convenience_function(cls: str) -> str:
    return f"""
def query(query_func: Callable, **kwargs: Any) -> {cls}:
{INDENT}\"\"\"
{INDENT}This is a convenience function which queries and parses the data into
{INDENT}concrete types. It should be compatible with most GQL clients.
{INDENT}You do not have to use it to consume the generated data classes.
{INDENT}Alternatively, you can also mime and alternate the behavior
{INDENT}of this function in the caller.

{INDENT}Parameters:
{INDENT}{INDENT}query_func (Callable): Function which queries your GQL Server
{INDENT}{INDENT}kwargs: optional arguments that will be passed to the query function

{INDENT}Returns:
{INDENT}{INDENT}{cls}: queried data parsed into generated classes
{INDENT}\"\"\"
{INDENT}raw_data: dict[Any, Any] = query_func(DEFINITION, **kwargs)
{INDENT}return {cls}(**raw_data)
"""


def mutation_convenience_function(cls: str) -> str:
    return f"""
def mutate(mutation_func: Callable, **kwargs: Any) -> {cls}:
{INDENT}\"\"\"
{INDENT}This is a convenience function which executes a mutation and parses the response
{INDENT}into concrete types. It should be compatible with most GQL clients.
{INDENT}You do not have to use it to consume the generated data classes.
{INDENT}Alternatively, you can also mime and alternate the behavior
{INDENT}of this function in the caller.

{INDENT}Parameters:
{INDENT}{INDENT}mutation_func (Callable): Function which executes the mutation.
{INDENT}{INDENT}kwargs: Arguments that will be passed to the mutation function.
{INDENT}{INDENT}{INDENT}This must include the mutation parameters.

{INDENT}Returns:
{INDENT}{INDENT}{cls}: mutation response parsed into generated classes
{INDENT}\"\"\"
{INDENT}raw_data: dict[Any, Any] = mutation_func(DEFINITION, **kwargs)
{INDENT}return {cls}(**raw_data)
"""


class PydanticV1Error(Exception):
    pass


class FieldToTypeMatcherVisitor(Visitor):
    def __init__(
        self,
        schema: GraphQLSchema,
        type_info: TypeInfo,
        definition: GQLDefinition,
        feature_flags: FeatureFlags,
    ) -> None:
        Visitor.__init__(self)
        self.schema = schema
        self.type_info = type_info
        self.definition = definition
        self.feature_flags = feature_flags
        self.parsed = ParsedNode(
            parent=None,
            fields=[],
            parsed_type=ParsedFieldType(
                unwrapped_python_type="",
                wrapped_python_type="",
                is_primitive=False,
                enum_map={},
            ),
        )
        self.parent: ParsedNode | None = self.parsed
        self.deduplication_cache: set[str] = set()

    def enter_inline_fragment(self, node: InlineFragmentNode, *_: Any) -> None:
        graphql_type = self.type_info.get_type()
        if not graphql_type:
            raise ValueError(f"{node} does not have a graphql type")
        field_type = self._parse_type(graphql_type=graphql_type)
        current = ParsedInlineFragmentNode(
            fields=[],
            parent=self.parent,
            parsed_type=field_type,
        )
        if not self.parent:
            raise ValueError("Parent is None")
        self.parent.fields.append(current)
        self.parent = current

    def leave_inline_fragment(self, *_: Any) -> None:
        self.parent = self.parent.parent if self.parent else self.parent

    def enter_operation_definition(
        self, node: OperationDefinitionNode, *_: Any
    ) -> None:
        if not node.name:
            raise ValueError(f"{node} does not have a name")
        current = ParsedOperationNode(
            parent=self.parent,
            fields=[],
            operation_type=self.definition.kind,
            parsed_type=ParsedFieldType(
                unwrapped_python_type=node.name.value,
                wrapped_python_type=node.name.value,
                is_primitive=False,
                enum_map={},
            ),
        )
        if not self.parent:
            raise ValueError("Parent is None")
        self.parent.fields.append(current)
        self.parent = current

    def leave_operation_definition(self, *_: Any) -> None:
        self.parent = self.parent.parent if self.parent else self.parent

    def enter_fragment_definition(self, node: FragmentDefinitionNode, *_: Any) -> None:
        graphql_type = self.type_info.get_type()
        if not graphql_type:
            raise ValueError(f"{node} does not have a graphql type")
        field_type = self._parse_type(graphql_type=graphql_type)
        name = graphql_class_name_str_to_python(node.name.value)
        current = ParsedFragmentDefinitionNode(
            fields=[],
            parent=self.parent,
            parsed_type=field_type,
            class_name=name,
            fragment_name=node.name.value,
        )
        if not self.parent:
            raise ValueError("Parent is None")
        self.parent.fields.append(current)
        self.parent = current

    def leave_fragment_definition(self, *_: Any) -> None:
        self.parent = self.parent.parent if self.parent else self.parent

    def enter_fragment_spread(self, node: FragmentSpreadNode, *_: Any) -> None:
        fragment_name = graphql_class_name_str_to_python(node.name.value)
        field_type = ParsedFieldType(
            is_primitive=False,
            unwrapped_python_type=fragment_name,
            wrapped_python_type=fragment_name,
            enum_map={},
        )
        current = ParsedFragmentSpreadNode(
            fields=[],
            parent=self.parent,
            parsed_type=field_type,
        )
        if not self.parent:
            raise ValueError("Parent is None")
        self.parent.fields.append(current)
        self.parent = current

    def leave_fragment_spread(self, *_: Any) -> None:
        self.parent = self.parent.parent if self.parent else self.parent

    def enter_field(self, node: FieldNode, *_: Any) -> None:
        graphql_type = self.type_info.get_type()
        if not graphql_type:
            raise ValueError(f"{node} does not have a graphql type")
        field_type = self._parse_type(graphql_type=graphql_type)
        gql_key = node.alias.value if node.alias else node.name.value
        py_key = graphql_field_name_to_python(gql_key)
        current = ParsedClassNode(
            fields=[],
            parent=self.parent,
            parsed_type=field_type,
            py_key=py_key,
            gql_key=gql_key,
        )
        if not self.parent:
            raise ValueError("Parent is None")
        self.parent.fields.append(current)
        self.parent = current

    def leave_field(self, *_: Any) -> None:
        self.parent = self.parent.parent if self.parent else self.parent

    # Custom Functions
    def _parse_type(self, graphql_type: GraphQLOutputType) -> ParsedFieldType:
        unwrapper_result = Unwrapper.unwrap(graphql_type)
        unwrapped_type = self._to_python_type(unwrapper_result.inner_gql_type)
        is_primitive = unwrapper_result.is_primitive
        enum_map = unwrapper_result.enum_map
        wrapped_type = unwrapped_type
        for wrapper in reversed(unwrapper_result.wrapper_stack):
            if wrapper == WrapperType.LIST:
                wrapped_type = f"list[{wrapped_type}]"
            elif wrapper == WrapperType.OPTIONAL:
                wrapped_type = f"Optional[{wrapped_type}]"

        return ParsedFieldType(
            unwrapped_python_type=unwrapped_type,
            wrapped_python_type=wrapped_type,
            is_primitive=is_primitive,
            enum_map=enum_map,
        )

    def _to_python_type(self, graphql_type: GraphQLOutputType) -> str:
        if isinstance(graphql_type, GraphQLScalarType):
            return graphql_primitive_to_python(
                graphql_type=graphql_type,
                custom_mappings=self.feature_flags.gql_scalar_mappings,
            )
        cur = self.parent
        class_name = graphql_class_name_to_python(graphql_type=graphql_type)
        collision_enum_suffix = 2

        # handle name collisions
        while cur and cur.parent and class_name in self.deduplication_cache:
            # Enumerate (1,2,3, ...) if you see a collision
            if (
                self.feature_flags.collision_strategy
                == NamingCollisionStrategy.ENUMERATE
            ):
                if collision_enum_suffix == 2:  # noqa: PLR2004
                    class_name = f"{class_name}__{collision_enum_suffix}"
                else:
                    idx = class_name.rfind("_") - 1
                    class_name = f"{class_name[:idx]}__{collision_enum_suffix}"
                collision_enum_suffix += 1
            # By default, prefix with parent name if you see a collision
            else:
                class_name = f"{cur.parsed_type.unwrapped_python_type}_{class_name}"
            cur = cur.parent

        self.deduplication_cache.add(class_name)
        return class_name


class QueryParser:
    @staticmethod
    def parse(
        definition: GQLDefinition, schema: GraphQLSchema, feature_flags: FeatureFlags
    ) -> ParsedNode:
        document_ast = parse(definition.definition)
        type_info = TypeInfo(schema)
        visitor = FieldToTypeMatcherVisitor(
            schema=schema,
            type_info=type_info,
            definition=definition,
            feature_flags=feature_flags,
        )
        visit(document_ast, TypeInfoVisitor(type_info, visitor))
        return visitor.parsed


class PydanticBase(Plugin):
    HEADER: str
    IMPORTS: str
    CONF: str

    def _traverse(self, node: ParsedNode) -> str:
        """Traverse the AST.

        Pydantic doesnt play well with from __future__ import annotations
        --> order of class declaration is important:
        - post-order for non-inline fragment nodes, i.e., non-interface nodes
        - pre-order for nodes that implement an interface
        """
        result = ""
        for child in node.fields:
            if not isinstance(child, ParsedInlineFragmentNode):
                result = f"{result}{self._traverse(child)}"

        result = f"{result}{node.class_code_string()}"

        for child in node.fields:
            if isinstance(child, ParsedInlineFragmentNode):
                result = f"{result}{self._traverse(child)}"
        return result

    def generate_fragments(
        self, definitions: list[GQLDefinition], schema: GraphQLSchema
    ) -> list[Fragment]:
        """Render all fragments.

        Handle nested fragments, i.e., fragments which
        depend on other fragments. The current dependency resolving approach
        is brute-force, but will get the job done for most likely use-cases.

        @TODO: fragment dependency graph should be calculated in pre-processor.
        This function should ideally then be able to process fragments in order.
        """
        processed: dict[str, Fragment] = {}
        current_to_process: list[GQLDefinition] = definitions
        next_to_process: list[GQLDefinition] = []
        while len(processed) < len(definitions):
            for definition in current_to_process:
                # We make sure that all dependencies are already rendered
                # in order to obtain proper import lines
                has_unrendered_dependencies = reduce(
                    operator.or_,
                    [dep not in processed for dep in definition.fragment_dependencies],
                    False,  # noqa: FBT003
                )
                if has_unrendered_dependencies:
                    # not all dependencies rendered yet. It will
                    # probably happen later in the loop, so we skip
                    # this and will try again in the next iteration.
                    next_to_process.append(definition)
                    continue
                fragment_imports = self._fragment_imports(
                    definition=definition,
                    fragment_map=processed,
                )
                result = self.HEADER + self.IMPORTS
                if fragment_imports:
                    result += "\n"
                    result += fragment_imports
                result += f"\n\n\n{self.CONF}"
                qf = definition.source_file
                parser = QueryParser()
                ast = parser.parse(
                    definition=definition,
                    schema=schema,
                    feature_flags=definition.feature_flags,
                )
                fragment = ast.fields[0]
                if not isinstance(fragment, ParsedFragmentDefinitionNode):
                    continue
                result += self._traverse(ast)
                result += "\n"
                import_path = str(definition.source_file.with_suffix("")).replace(
                    "/", "."
                )
                rendered_fragment = Fragment(
                    definition=definition,
                    file=qf.with_suffix(".py"),
                    content=result,
                    class_name=fragment.class_name,
                    import_path=import_path,
                    fragment_name=fragment.fragment_name,
                )
                processed[rendered_fragment.fragment_name] = rendered_fragment

            if len(current_to_process) == len(next_to_process):
                # We found a cyclic dependency, i.e., not a single
                # fragment got rendered in this iteration
                raise PydanticV1Error("Cyclic fragment dependency detected")

            # lets try again to render all fragments that we skipped in this iteration
            current_to_process = next_to_process
            next_to_process = []

        return list(processed.values())

    @staticmethod
    def _fragment_imports(
        definition: GQLDefinition, fragment_map: Mapping[str, Fragment]
    ) -> str:
        imports = ""
        for dep in sorted(definition.fragment_dependencies):
            fragment = fragment_map[dep]
            imports += f"\nfrom {fragment.import_path} import {fragment.class_name}"
        return imports

    def _assemble_definition(
        self,
        definition: GQLDefinition,
        fragment_definitions: Mapping[str, GQLDefinition],
    ) -> set[str]:
        ans: set[str] = set()
        ans.add(definition.definition)
        for dep in sorted(definition.fragment_dependencies):
            ans = ans.union(
                self._assemble_definition(
                    definition=fragment_definitions[dep],
                    fragment_definitions=fragment_definitions,
                )
            )
        return ans

    def generate_operations(
        self,
        definitions: list[GQLDefinition],
        schema: GraphQLSchema,
        fragments: list[Fragment],
    ) -> list[GeneratedFile]:
        generated_files: list[GeneratedFile] = []
        fragment_map = {f.fragment_name: f for f in fragments}
        fragment_definitions = {f.fragment_name: f.definition for f in fragments}
        for definition in definitions:
            fragment_imports = self._fragment_imports(
                definition=definition,
                fragment_map=fragment_map,
            )

            result = self.HEADER + self.IMPORTS
            if fragment_imports:
                result += "\n"
                result += fragment_imports
            result += "\n\n\n"
            qf = definition.source_file
            assembled_definition = "\n\n".join(
                sorted(
                    self._assemble_definition(
                        definition=definition,
                        fragment_definitions=fragment_definitions,
                    )
                )
            )
            result += f'DEFINITION = """\n{assembled_definition}\n"""'
            result += f"\n\n\n{self.CONF}"
            parser = QueryParser()
            ast = parser.parse(
                definition=definition,
                schema=schema,
                feature_flags=definition.feature_flags,
            )
            result += self._traverse(ast)
            result += "\n\n"
            cls = ast.fields[0].parsed_type.unwrapped_python_type
            if definition.kind == GQLDefinitionType.QUERY:
                result += query_convenience_function(cls=f"{cls}QueryData")
            else:
                result += mutation_convenience_function(cls=f"{cls}MutationResponse")
            generated_files.append(
                GeneratedFile(file=qf.with_suffix(".py"), content=result)
            )

        return generated_files


class PydanticV1Plugin(PydanticBase):
    """Pydantic v1 plugin for Qenerate."""

    HEADER = (
        '"""\nGenerated by qenerate plugin=pydantic_v1. DO NOT MODIFY MANUALLY!\n"""\n'
    )

    IMPORTS = (
        "from collections.abc import Callable  # noqa: F401 # pylint: disable=W0611\n"
        "from datetime import datetime  # noqa: F401 # pylint: disable=W0611\n"
        "from enum import Enum  # noqa: F401 # pylint: disable=W0611\n"
        "from typing import (  # noqa: F401 # pylint: disable=W0611\n"
        f"{INDENT}Any,\n"
        f"{INDENT}Optional,\n"
        f"{INDENT}Union,\n"
        ")\n"
        "\n"
        "from pydantic import (  # noqa: F401 # pylint: disable=W0611\n"
        f"{INDENT}BaseModel,\n"
        f"{INDENT}Extra,\n"
        f"{INDENT}Field,\n"
        f"{INDENT}Json,\n"
        ")"
    )

    CONF = (
        f"class {BASE_CLASS_NAME}(BaseModel):\n"
        f"{INDENT}class Config:\n"
        # https://pydantic-docs.helpmanual.io/usage/model_config/#smart-union
        # https://stackoverflow.com/a/69705356/4478420
        f"{INDENT}{INDENT}smart_union=True\n"
        f"{INDENT}{INDENT}extra=Extra.forbid"
    )


class PydanticV2Plugin(PydanticBase):
    """Pydantic v2 plugin for Qenerate."""

    HEADER = (
        '"""\nGenerated by qenerate plugin=pydantic_v2. DO NOT MODIFY MANUALLY!\n"""\n'
    )

    IMPORTS = (
        "from collections.abc import Callable  # noqa: F401 # pylint: disable=W0611\n"
        "from datetime import datetime  # noqa: F401 # pylint: disable=W0611\n"
        "from enum import Enum  # noqa: F401 # pylint: disable=W0611\n"
        "from typing import (  # noqa: F401 # pylint: disable=W0611\n"
        f"{INDENT}Any,\n"
        f"{INDENT}Optional,\n"
        f"{INDENT}Union,\n"
        ")\n"
        "\n"
        "from pydantic import (  # noqa: F401 # pylint: disable=W0611\n"
        f"{INDENT}BaseModel,\n"
        f"{INDENT}ConfigDict,\n"
        f"{INDENT}Field,\n"
        f"{INDENT}Json,\n"
        ")"
    )

    CONF = (
        f"class {BASE_CLASS_NAME}(BaseModel):\n"
        f"{INDENT}model_config = ConfigDict(\n"
        f"{INDENT}{INDENT}extra='forbid'\n"
        f"{INDENT})"
    )
