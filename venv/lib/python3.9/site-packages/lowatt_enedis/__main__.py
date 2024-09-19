# Copyright (c) 2021 by Lowatt - info@lowatt.fr
#
# This program is part of lowatt_enedis
#
# lowatt_enedis is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# lowatt_enedis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with lowatt_enedis.  If not, see <https://www.gnu.org/licenses/>.
import argparse
import sys
from typing import NoReturn

from suds.client import Client

import lowatt_enedis.services  # noqa: register services
from lowatt_enedis import (
    COMMAND_SERVICE,
    WSException,
    arg_from_env,
    handle_cli_command,
    init_cli,
    wsdl,
)

from . import decrypt


def _cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CLI access to Enedis SGE web-services.",
    )

    subparsers = parser.add_subparsers(dest="command")
    init_cli(subparsers)

    # wsdl command
    subparser = subparsers.add_parser(
        "wsdl",
        help="Display WSDL information about some ws command.",
    )
    subparser.add_argument(
        "service_command",
        help="Command name.",
    )

    # decrypt command
    subparser = subparsers.add_parser(
        "decrypt",
        help="Decrypt AES-128-CBC enedis files",
    )
    subparser.add_argument(
        "--key",
        help="Hex AES key",
        **arg_from_env("ENEDIS_DECRYPT_KEY"),
    )
    subparser.add_argument(
        "--iv",
        help="Hex CBC IV",
        **arg_from_env("ENEDIS_DECRYPT_IV"),
    )
    subparser.add_argument(
        "input_file", help="Input file", type=argparse.FileType("rb")
    )
    subparser.add_argument(
        "-o",
        "--output",
        help="Output file",
        required=True,
    )

    return parser


def run() -> NoReturn:
    parser = _cli_parser()
    args = parser.parse_args()

    if args.command == "wsdl":
        try:
            service_name = COMMAND_SERVICE[args.service_command][0]
        except KeyError:
            service_name = args.service_command

        print(Client(wsdl(service_name)))  # noqa

    elif args.command == "decrypt":
        decrypted = decrypt.decrypt_aes_128_cbc(args.key, args.iv, args.input_file)
        with open(args.output, "wb") as f:
            f.write(decrypted)
    elif args.command:
        try:
            handle_cli_command(args.command, args)
        except WSException:
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    run()
