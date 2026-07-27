import json

import requests
from graphql import get_introspection_query


class IntrospectionCommand:
    @staticmethod
    def introspection_query(url: str) -> None:
        query = get_introspection_query()
        request = requests.post(url, json={"query": query}, timeout=30)
        if request.status_code == requests.codes.ok:
            print(json.dumps(request.json(), indent=4))  # ruff: ignore[print]
            return
        raise Exception(f"Could not query {url}")  # ruff: ignore[raise-vanilla-class]
