import re

from graphql import GraphQLOutputType


def _keyword_sanitizer(s: str) -> str:
    keyword_remapping = {
        "global": "q_global",
        "from": "q_from",
        "type": "q_type",
        "id": "q_id",
        "to": "q_to",
        "format": "q_format",
    }
    if s in keyword_remapping:
        return keyword_remapping[s]
    return s


def graphql_class_name_to_python(graphql_type: GraphQLOutputType) -> str:
    class_name = str(graphql_type)
    result = class_name[0]
    for i in range(1, len(class_name)):
        cur, prev = class_name[i], class_name[i - 1]
        if cur != "_" and prev != "_":
            result += cur
        elif cur != "_" and prev == "_":
            result += cur.upper()
    return result


def graphql_primitive_to_python(graphql_type: GraphQLOutputType) -> str:
    mapping = {
        "ID": "str",
        "String": "str",
        "Int": "int",
        "Float": "float",
        "Boolean": "bool",
        "DateTime": "DateTime",
        "JSON": "Json",
    }
    return mapping.get(str(graphql_type), str(graphql_type))


def graphql_field_name_to_python(name: str) -> str:
    # ElbFQDN -> ["elb", "f", "q", "d", "n"]
    parts = re.split("(?=[A-Z])", name)
    for i, el in enumerate(parts):
        parts[i] = el.lower()

    # ["elb", "f", "q", "d", "n"] -> elb_fqdn
    result = parts[0]
    for i in range(1, len(parts)):
        cur, prev = parts[i], parts[i - 1]
        if len(cur) == 1 and len(prev) == 1:
            result += cur
        else:
            result += f"_{cur}"
    return _keyword_sanitizer(result)
