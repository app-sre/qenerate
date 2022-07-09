from dataclasses import dataclass
from typing import Any, Mapping


@dataclass
class Fragment:
    class_name: str
    import_package: str
    gql_query: str


@dataclass
class FragmentGeneratorResult:
    code: str
    fragments: dict[str, Fragment]


class Plugin:
    def generate_query_classes(
        self,
        query: str,
        raw_schema: Mapping[Any, Any],
        fragments: Mapping[str, Fragment],
    ) -> str:
        raise NotImplementedError

    def generate_fragment_classes(
        self,
        fragment: str,
        raw_schema: Mapping[Any, Any],
        import_package: str,
    ) -> FragmentGeneratorResult:
        raise NotImplementedError
