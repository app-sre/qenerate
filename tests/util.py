import json


def get_result(plugin: str, filename: str) -> str:
    with open(f"tests/queries/expected/{plugin}/{filename}") as f:
        return f.read()


def get_introspection() -> dict:
    with open(f"tests/queries/introspection.json") as f:
        return json.loads(f.read())["data"]


def get_query(filename: str) -> str:
    with open(f"tests/queries/{filename}") as f:
        return f.read()


def get_fragment(filename: str) -> str:
    with open(f"tests/fragments/{filename}") as f:
        return f.read()
