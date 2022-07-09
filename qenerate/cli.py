import argparse
from qenerate.core.code_command import CodeCommand, CodeCommandArgs

from qenerate.core.introspection_command import IntrospectionCommand


def run():
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
    parser_generator.add_argument(
        "-i",
        dest="introspection",
        type=str,
        help="Specify introspection query json",
    )
    parser_generator.add_argument(
        "-q",
        dest="queries",
        type=str,
        help=(
            "Specify directory with queries. " "The directory is traversed recursively."
        ),
    )
    parser_generator.add_argument(
        "-f",
        dest="fragments",
        type=str,
        help=(
            "Specify directory with fragments. "
            "The directory is traversed recursively."
        ),
    )
    parser_generator.add_argument(
        "-p",
        dest="fragments_package_prefix",
        type=str,
        help=(
            "The package prefix used to generate fragment imports. "
            "E.g., -p my.package would result in "
            "from my.package.path.to.fragment import MyFragment"
        ),
    )

    args = parser.parse_args()

    if args.subcommand == "introspection":
        IntrospectionCommand.introspection_query(args.url)
    elif args.subcommand == "code":
        CodeCommand.generate_code(
            CodeCommandArgs(
                introspection_file_path=args.introspection,
                fragments_dir=args.fragments,
                queries_dir=args.queries,
                fragments_package_prefix=args.fragments_package_prefix,
            )
        )


if __name__ == "__main__":
    run()
