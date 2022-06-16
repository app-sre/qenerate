import json
import requests

from graphql import get_introspection_query


def query_schema(url: str):
    query = get_introspection_query()
    request = requests.post(url, json={"query": query})
    if request.status_code == 200:
        print(json.dumps(request.json(), indent=4))
        return
    raise Exception(f"Could not query {url}")
