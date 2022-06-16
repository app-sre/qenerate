import argparse

from qenerate.core.introspection import introspection_query


parser = argparse.ArgumentParser(prog="qenerate")
subparsers = parser.add_subparsers(help="Supported commands", dest="subcommand")

parser_introspection = subparsers.add_parser(
    "introspection",
    help="Run introspection query on given GQL URL.",
)
parser_introspection.add_argument("url", type=str, help="URL to run query against")

parser_generator = subparsers.add_parser(
    "code",
    help="Generate Code",
)
parser_generator.add_argument("-i", type=str, help="Specify introspection query json")

args = parser.parse_args()

if args.subcommand == "introspection":
    introspection_query(args.url)
elif args.subcommand == "code":
    print("TODO")
