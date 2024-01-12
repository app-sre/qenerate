from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from qenerate.core.preprocessor import GQLDefinitionType

BASE_CLASS_NAME = "ConfiguredBaseModel"
INDENT = "    "


@dataclass
class ParsedNode:
    parent: Optional[ParsedNode]
    fields: list[ParsedNode]
    parsed_type: ParsedFieldType

    def class_code_string(self) -> str:
        return ""

    def _needs_class_rendering(self) -> bool:
        if self.parsed_type.is_primitive:
            return False

        return not self._is_non_partial_fragment()

    def _is_non_partial_fragment(self) -> bool:
        return len(self.fields) == 1 and isinstance(
            self.fields[0], ParsedFragmentSpreadNode
        )

    def _empty(self) -> str:
        return f"{INDENT}..."


@dataclass
class ParsedInlineFragmentNode(ParsedNode):
    def class_code_string(self) -> str:
        # Assure not Optional[]
        if not (self.parent and self.parsed_type):
            return ""

        if self.parsed_type.is_primitive:
            return ""

        base_class = self.parent.parsed_type.unwrapped_python_type
        if isinstance(self.parent, ParsedFragmentDefinitionNode):
            base_class = self.parent.fragment_name

        lines = ["\n\n"]
        lines.append(
            ("class " f"{self.parsed_type.unwrapped_python_type}" f"({base_class}):")
        )
        fields_added = False
        for field in self.fields:
            if isinstance(field, ParsedClassNode):
                lines.append(
                    (
                        f"{INDENT}{field.py_key}: {field.field_type()} = "
                        f'Field(..., alias="{field.gql_key}")'
                    )
                )
                fields_added = True

        if not fields_added:
            lines.append(self._empty())

        return "\n".join(lines)


@dataclass
class ParsedClassNode(ParsedNode):
    gql_key: str
    py_key: str

    def class_code_string(self) -> str:
        if not self._needs_class_rendering():
            return ""

        if self.parsed_type.enum_map:
            return self._enum_code()
        else:
            return self._class_code()

    def _class_code(self) -> str:
        base_classes = ", ".join(self._base_classes())
        lines = ["\n\n"]
        lines.append(f"class {self.parsed_type.unwrapped_python_type}({base_classes}):")
        fields_added = False
        for field in self.fields:
            field_arg = "..., "
            if field.parsed_type.enum_map:
                field_arg = ""
            if isinstance(field, ParsedClassNode):
                lines.append(
                    (
                        f"{INDENT}{field.py_key}: {field.field_type()} = "
                        f'Field({field_arg}alias="{field.gql_key}")'
                    )
                )
                fields_added = True

        if not fields_added:
            lines.append(self._empty())

        return "\n".join(lines)

    def _enum_code(self) -> str:
        lines = ["\n\n"]
        lines.append(f"class {self.parsed_type.unwrapped_python_type}(Enum):")
        for k, v in self.parsed_type.enum_map.items():
            val = f'"{v}"' if isinstance(v, str) else v
            lines.append(f"{INDENT}{k} = {val}")
        return "\n".join(lines)

    def _base_classes(self) -> list[str]:
        base_classes: list[str] = []
        for field in self.fields:
            if not isinstance(field, ParsedFragmentSpreadNode):
                continue
            base_classes.append(field.parsed_type.unwrapped_python_type)
        if not base_classes:
            base_classes.append(BASE_CLASS_NAME)
        return base_classes

    def field_type(self) -> str:
        # This is a full (non-partial) fragment spread
        if len(self.fields) == 1 and isinstance(
            self.fields[0], ParsedFragmentSpreadNode
        ):
            return self.parsed_type.wrapped_python_type.replace(
                self.parsed_type.unwrapped_python_type,
                self.fields[0].parsed_type.unwrapped_python_type,
            )

        unions: list[str] = []
        # TODO: sorting does not need to happen on each call
        """
        Pydantic does best-effort matching on Unions.
        Declare most significant type first.
        This, smart_union and disallowing extra fields gives high confidence
        in matching.
        https://pydantic-docs.helpmanual.io/usage/types/#unions
        """
        self.fields.sort(key=lambda a: len(a.fields), reverse=True)
        for field in self.fields:
            if isinstance(field, ParsedInlineFragmentNode):
                unions.append(field.parsed_type.unwrapped_python_type)
        if len(unions) > 0:
            unions.append(self.parsed_type.unwrapped_python_type)
            return self.parsed_type.wrapped_python_type.replace(
                self.parsed_type.unwrapped_python_type, f"Union[{', '.join(unions)}]"
            )
        return self.parsed_type.wrapped_python_type


@dataclass
class ParsedOperationNode(ParsedNode):
    operation_type: GQLDefinitionType

    def class_code_string(self) -> str:
        lines = ["\n\n"]
        class_suffix = "QueryData"
        if self.operation_type == GQLDefinitionType.MUTATION:
            class_suffix = "MutationResponse"
        lines.append(
            f"class {self.parsed_type.unwrapped_python_type}{class_suffix}"
            f"({BASE_CLASS_NAME}):"
        )
        fields_added = False
        for field in self.fields:
            if isinstance(field, ParsedClassNode):
                lines.append(
                    (
                        f"{INDENT}{field.py_key}: {field.field_type()} = "
                        f'Field(..., alias="{field.gql_key}")'
                    )
                )
                fields_added = True

        if not fields_added:
            lines.append(self._empty())

        return "\n".join(lines)


@dataclass
class ParsedFragmentDefinitionNode(ParsedNode):
    class_name: str
    fragment_name: str

    def class_code_string(self) -> str:
        lines = ["\n\n"]
        lines.append(f"class {self.class_name}({BASE_CLASS_NAME}):")
        fields_added = False
        for field in self.fields:
            if isinstance(field, ParsedClassNode):
                lines.append(
                    (
                        f"{INDENT}{field.py_key}: {field.field_type()} = "
                        f'Field(..., alias="{field.gql_key}")'
                    )
                )
                fields_added = True

        if not fields_added:
            lines.append(self._empty())

        return "\n".join(lines)


@dataclass
class ParsedFragmentSpreadNode(ParsedNode):
    def class_code_string(self) -> str:
        return ""


@dataclass
class ParsedFieldType:
    unwrapped_python_type: str
    wrapped_python_type: str
    is_primitive: bool
    enum_map: dict[str, Any]
