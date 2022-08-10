import json
from pathlib import Path

import pytest
from qenerate.core.plugin import GeneratedFile


@pytest.fixture()
def expected_files():
    """Read fixture files from test/queries/expected/PLUGIN/QUERY and remove .txt suffix."""

    def _(plugin: str, query: str) -> list[GeneratedFile]:
        return sorted(
            [
                GeneratedFile(file=f.with_suffix(""), content=f.read_text())
                for f in Path(f"tests/queries/expected/{plugin}/{query}").glob("**/*")
            ]
        )

    return _


@pytest.fixture()
def schema_raw():
    with open("tests/queries/introspection.json") as f:
        return json.loads(f.read())["data"]
