import json


def get_query(filename: str) -> str:
    with open(f"tests/queries/{filename}") as f:
        return f.read()


def get_result(plugin: str, filename: str) -> str:
    with open(f"tests/queries/expected/{plugin}/{filename}") as f:
        return f.read()


def get_introspection() -> dict:
    with open(f"tests/queries/introspection.json") as f:
        return json.loads(f.read())["data"]
