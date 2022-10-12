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
    return graphql_class_name_str_to_python(str(graphql_type))


def graphql_class_name_str_to_python(class_name: str) -> str:
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
    # SLOParameter -> ["s", "l", "o", "parameter"]
    parts = re.split("(?=[A-Z])", name)
    if not parts[0]:
        # if first letter was capital, then split will add '' first
        parts = parts[1:]
    for i, el in enumerate(parts):
        parts[i] = el.lower()

    # ["elb", "f", "q", "d", "n"] -> elb_fqdn
    # ["s", "l", "o", "parameter"] -> slo_parameter
    result = parts[0]
    for i in range(1, len(parts)):
        cur, prev = parts[i], parts[i - 1]
        if len(cur) == 1 and len(prev) == 1:
            result += cur
        else:
            result += f"_{cur}"
    return _keyword_sanitizer(result)
