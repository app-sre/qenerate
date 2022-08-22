from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


INDENT = "    "


@dataclass
class ParsedNode:
    parent: Optional[ParsedNode]
    fields: list[ParsedNode]
    parsed_type: ParsedFieldType

    def class_code_string(self) -> str:
        return ""

    def _pydantic_config_string(self) -> list[str]:
        # https://pydantic-docs.helpmanual.io/usage/model_config/#smart-union
        # https://stackoverflow.com/a/69705356/4478420
        lines: list[str] = []
        lines.append(f"{INDENT}class Config:")
        lines.append(f"{INDENT}{INDENT}smart_union = True")
        lines.append(f"{INDENT}{INDENT}extra = Extra.forbid")
        return lines


@dataclass
class ParsedInlineFragmentNode(ParsedNode):
    def class_code_string(self) -> str:
        # Assure not Optional[]
        if not (self.parent and self.parsed_type):
            return ""

        if self.parsed_type.is_primitive:
            return ""

        lines = ["\n\n"]
        lines.append(
            (
                "class "
                f"{self.parsed_type.unwrapped_python_type}"
                f"({self.parent.parsed_type.unwrapped_python_type}):"
            )
        )
        for field in self.fields:
            if isinstance(field, ParsedClassNode):
                lines.append(
                    (
                        f"{INDENT}{field.py_key}: {field.field_type()} = "
                        f'Field(..., alias="{field.gql_key}")'
                    )
                )

        lines.append("")
        lines.extend(self._pydantic_config_string())

        return "\n".join(lines)


@dataclass
class ParsedClassNode(ParsedNode):
    gql_key: str
    py_key: str

    def class_code_string(self) -> str:
        if self.parsed_type.is_primitive:
            return ""

        lines = ["\n\n"]
        lines.append(f"class {self.parsed_type.unwrapped_python_type}(BaseModel):")
        for field in self.fields:
            if isinstance(field, ParsedClassNode):
                lines.append(
                    (
                        f"{INDENT}{field.py_key}: {field.field_type()} = "
                        f'Field(..., alias="{field.gql_key}")'
                    )
                )

        lines.append("")
        lines.extend(self._pydantic_config_string())

        return "\n".join(lines)

    def field_type(self) -> str:
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
    def class_code_string(self) -> str:
        lines = ["\n\n"]
        lines.append(
            f"class {self.parsed_type.unwrapped_python_type}QueryData(BaseModel):"
        )
        for field in self.fields:
            if isinstance(field, ParsedClassNode):
                lines.append(
                    (
                        f"{INDENT}{field.py_key}: {field.field_type()} = "
                        f'Field(..., alias="{field.gql_key}")'
                    )
                )

        lines.append("")
        lines.extend(self._pydantic_config_string())

        return "\n".join(lines)


@dataclass
class ParsedFragmentDefinitionNode(ParsedNode):
    class_name: str
    fragment_name: str

    def class_code_string(self) -> str:
        lines = ["\n\n"]
        lines.append(f"class {self.class_name}(BaseModel):")
        for field in self.fields:
            if isinstance(field, ParsedClassNode):
                lines.append(
                    (
                        f"{INDENT}{field.py_key}: {field.field_type()} = "
                        f'Field(..., alias="{field.gql_key}")'
                    )
                )

        lines.append("")
        lines.extend(self._pydantic_config_string())
        return "\n".join(lines)


@dataclass
class ParsedFieldType:
    unwrapped_python_type: str
    wrapped_python_type: str
    is_primitive: bool
