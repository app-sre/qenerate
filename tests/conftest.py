import json
import locale
from pathlib import Path
from typing import cast

import pytest
from graphql import IntrospectionQuery, build_client_schema

from qenerate.core.plugin import GeneratedFile


@pytest.fixture()
def expected_files():
    """Read fixture files from tests/definitions/expected/PLUGIN/CASE and remove .txt suffix."""

    def _(plugin: str, case: str) -> list[GeneratedFile]:
        return sorted([
            GeneratedFile(file=f.with_suffix(""), content=f.read_text())
            for f in Path(f"tests/generator/expected/{plugin}/{case}").glob("**/*")
        ])

    return _


@pytest.fixture()
def app_interface_schema():
    with open(
        "tests/generator/introspection-app-interface.json",
        encoding=locale.getpreferredencoding(False),
    ) as f:
        raw_schema = json.loads(f.read())["data"]
    return build_client_schema(cast(IntrospectionQuery, raw_schema))


@pytest.fixture()
def app_interface_2023_03_schema():
    with open(
        "tests/generator/introspection-app-interface_2023_03.json",
        encoding=locale.getpreferredencoding(False),
    ) as f:
        raw_schema = json.loads(f.read())["data"]
    return build_client_schema(cast(IntrospectionQuery, raw_schema))


@pytest.fixture()
def github_schema():
    with open(
        "tests/generator/introspection-github.json",
        encoding=locale.getpreferredencoding(False),
    ) as f:
        raw_schema = json.loads(f.read())["data"]
    return build_client_schema(cast(IntrospectionQuery, raw_schema))
