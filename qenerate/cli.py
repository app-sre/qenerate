import argparse

import pkg_resources  # type: ignore

from qenerate.core.code_command import CodeCommand
from qenerate.core.introspection_command import IntrospectionCommand
from qenerate.core.preprocessor import Preprocessor


def run():
    parser = argparse.ArgumentParser(prog="qenerate")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=pkg_resources.require("qenerate")[0].version,
    )

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
        "dir", type=str, help="Specify introspection query json"
    )

    args = parser.parse_args()

    if args.subcommand == "introspection":
        IntrospectionCommand.introspection_query(args.url)
    elif args.subcommand == "code":
        code_command = CodeCommand(preprocessor=Preprocessor())
        code_command.generate_code(
            introspection_file_path=args.introspection,
            dir=args.dir,
        )


if __name__ == "__main__":
    run()
