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
"""
`lowatt_enedis`
---------------

Command line interface to enedis SGE web-services.
"""

import argparse
import datetime
import json
import logging
import os
import sys
import xml.dom.minidom
from functools import wraps
from pathlib import Path, PurePath
from typing import Any, Callable, Iterator, Optional, TypeVar, Union

import rich
import suds.sudsobject
from suds import WebFault
from suds.client import Client
from suds.plugin import DocumentPlugin

from .certauth import HTTPSClientCertTransport

RT = TypeVar("RT")

logging.basicConfig(level=logging.INFO)
# send raw enedis errors to stderr:
errHandler = logging.StreamHandler(sys.stderr)
logging.getLogger("suds.client").addHandler(errHandler)
logging.getLogger("suds.client").propagate = False
# logging.getLogger("suds.client").setLevel(logging.DEBUG)
# logging.getLogger("suds.resolver").setLevel(logging.DEBUG)
# logging.getLogger("suds.mx").setLevel(logging.DEBUG)
# logging.getLogger("suds.transport").setLevel(logging.DEBUG)


WSDL_DIR = PurePath(__file__).parent.joinpath("wsdl")
SERVICES = {x.stem: x.resolve().as_uri() for x in Path(WSDL_DIR).glob("**/*.wsdl")}
COMMAND_SERVICE: dict[str, tuple[str, dict[str, Any], Any]] = {}


def wsdl(service_name: str) -> str:
    """Return path to WSDL file for `service_name`."""
    try:
        return SERVICES[service_name]
    except KeyError:
        raise KeyError(
            "Unknown service name {!r}, available services are {}".format(
                service_name,
                ", ".join(sorted(SERVICES)),
            ),
        ) from None


def arg_from_env(key: str) -> dict[str, Any]:
    default = os.environ.get(key)
    return {"default": default, "required": not default}


def init_cli(subparsers: Any) -> None:
    """Init CLI subparsers according to registered services."""
    for command, (service, options, _) in COMMAND_SERVICE.items():
        subparser = subparsers.add_parser(
            command,
            help='Query the "{}" web-service.'.format(service),
        )
        subparser.add_argument(
            "--login",
            help="User login. Default to ENEDIS_LOGIN environment variable.",
            **arg_from_env("ENEDIS_LOGIN"),
        )
        for option_name, option_kwargs in options.items():
            subparser.add_argument(option_name, **option_kwargs)

        subparser.add_argument(
            "--cert-file",
            help="Client certificate file. Default to ENEDIS_CERT_FILE environment variable.",
            **arg_from_env("ENEDIS_CERT_FILE"),
        )
        subparser.add_argument(
            "--key-file",
            help="Client private key file. Default to ENEDIS_KEY_FILE environment variable.",
            **arg_from_env("ENEDIS_KEY_FILE"),
        )
        subparser.add_argument(
            "--homologation",
            default="ENEDIS_HOMOLOGATION" in os.environ,
            action="store_true",
            help=(
                "Change service host to use homologation sandbox. "
                "Enabled by presence of ENEDIS_HOMOLOGATION in environment variables."
            ),
        )
        subparser.add_argument(
            "--output",
            choices=["xml", "json"],
            default="xml",
            help="Output type. Default is xml",
        )


def json_encode_default(obj: Any) -> Any:
    if isinstance(obj, suds.sudsobject.Object):
        return suds.sudsobject.asdict(obj)
    elif isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    raise TypeError(f"Object {obj!r} is not JSON serializable")


class WSException(Exception):
    """Exception raised for ws excpetion with fault details.

    Attributes:
        exc -- the original WebFault object
        code -- the error code (if parsable)
        message -- the error message
    """

    def __init__(self, exc: WebFault):
        self.web_fault = exc
        fault = exc.fault
        try:
            res = fault.detail.erreur.resultat
            self.message = str(res.value)
            self.code: Optional[str] = str(res._code)
        except AttributeError:
            if "faultcode" in fault and "faultstring" in fault:
                self.code = str(fault.faultcode)
                self.message = str(fault.faultstring)
            else:
                # Unable to find message in 'Fault' object,
                # at least when server's response isn't properly parseable.
                self.code = None
                self.message = str(exc)

    def __str__(self) -> str:
        if self.code:
            return f"{self.code}: {self.message}"
        return self.message


def pretty_xml(input_xml: str) -> str:
    output_xml = xml.dom.minidom.parseString(input_xml).toprettyxml(indent="  ")
    return "\n".join(line for line in output_xml.split("\n") if line.strip())


def handle_cli_command(command: str, args: argparse.Namespace) -> None:
    """Run `command` service using configuration in `args`."""
    service, _, handler = COMMAND_SERVICE[command]
    client = get_client(service, args.cert_file, args.key_file, args.homologation)
    if args.output == "xml":
        client.options.retxml = True
    try:
        obj = handler(client, args)
    except WSException as exc:
        if args.output == "json":
            rich.print_json(
                json.dumps(
                    {"errcode": exc.code, "errmsg": exc.message},
                    indent=2,
                    default=json_encode_default,
                    sort_keys=True,
                )
            )
        else:
            rich.print(pretty_xml(exc.web_fault.document.str()))
        raise
    else:
        if args.output == "json":
            rich.print_json(
                json.dumps(obj, indent=2, default=json_encode_default, sort_keys=True)
            )
        else:
            rich.print(pretty_xml(obj.decode()))


def get_client(
    service: str, cert_file: str, key_file: str, homologation: bool = False
) -> Client:
    # Need custom plugin to handle `xs:choice` potentially expected in service
    # arguments. Non-handling this seems to be an outstanding suds bug, see
    # https://stackoverflow.com/questions/5963404/suds-and-choice-tag
    client = Client(
        wsdl(service),
        plugins=[_SetChoicePlugin()],
        transport=HTTPSClientCertTransport(cert_file, key_file),
    )
    # XXX unclear why this has to be done to properly consider port's
    # location. If not, options'location is set to WSDL url and override the
    # port's location.
    client.set_options(location=None)

    for method in iter_methods(client):
        # some services are still using .erdf.fr domain, but it's
        # misconfigured and use .enedis.fr certificate causing
        # verification failure.
        method.location = method.location.replace(b".erdf.fr", b".enedis.fr")

        # ConsultationMesuresDetaillees location is also misconfigured
        if (
            method.location
            == b"http://www.enedis.fr/sge/b2b/services/consultationmesuresdetaillees/v2.0"
        ):
            method.location = (
                b"https://sge-b2b.enedis.fr/ConsultationMesuresDetaillees/v2.0"
            )

        if homologation:
            method.location = method.location.replace(
                b"/sge-b2b.",
                b"/sge-homologation-b2b.",
            )

    return client


class _SetChoicePlugin(DocumentPlugin):  # type: ignore[misc]
    def __init__(self) -> None:
        self.choosen_tags = {"autorisationClient"}

    def parsed(self, context: suds.plugin.DocumentContext) -> None:
        self._rec_set_choices(context.document)

    def _rec_set_choices(self, document: suds.sax.element.Element) -> None:
        for i in document.children:
            if i.name == "choice":
                for j in i.children:
                    if j.getAttribute("name").value in self.choosen_tags:
                        i.parent.append(j)

            else:
                # recursion
                self._rec_set_choices(i)


def register(
    command: str, service: str, options: dict[str, Any]
) -> Callable[[Callable[..., RT]], Callable[..., RT]]:
    """Decorator registering function as a service handler for CLI `command`,
    matching `service` web-service name, accepting `options` (list of dict given
    to `argparse.ArgumentParser.add_argument`)

    """

    def decorator(func: Callable[..., RT]) -> Callable[..., RT]:
        COMMAND_SERVICE[command] = (service, options, func)
        return func

    return decorator


def ws(service: str) -> Callable[[Callable[..., RT]], Callable[..., RT]]:
    """Decorator around sge web service call, returning a wrapper that properly set
    SOAP headers required by the service

    """

    def decorator(func: Callable[..., RT]) -> Callable[..., RT]:
        @wraps(func)
        def call_service(client: Client, args: argparse.Namespace) -> RT:
            # Headers are not consistent among webservices. If the
            # following gets more convoluted, maybe we should not try to
            # make it generic.

            # Expect a single service with a single port with a single method
            methods = client.wsdl.services[0].ports[0].methods
            assert len(methods) == 1
            method = next(iter(methods.values()))
            # Check if the method uses a header
            headers = method.soap.input.headers
            if len(headers) == 1:
                header_name, header_ns = headers[0].part.element
                header_element = "{" + header_ns + "}" + header_name
                header = client.factory.create(header_element)
                if "version" in header:
                    header.version = service.split("-")[1][1:]
                header.infoDemandeur.loginDemandeur = get_option(args, "login")
                client.set_options(soapheaders=header)

            try:
                return func(client, args)
            except WebFault as exc:
                raise WSException(exc)

        return call_service

    return decorator


def create_from_options(
    client: Client,
    args: argparse.Namespace,
    xstype_name: str,
    options_map: dict[str, str],
) -> Optional[suds.sudsobject.Object]:
    """Create and return an `xstype_name` element, and fill it according to
    `options_map` {arg name: xs element name}` mapping by looking for value in
    command line `args`.

    """
    if not hasattr(client, "xstypes_map"):
        client.xstypes_map = build_xstypes_map(client)
    xstype, prefix = client.xstypes_map[xstype_name]
    children_map = xstype_children_map(xstype)
    instance = client.factory.create("{}:{}".format(prefix, xstype_name))

    has_value = False
    for option in options_map:
        value = get_option(args, option)

        element_name = options_map[option]
        try:
            element = children_map[element_name]
        except KeyError as exc:
            exc.args = ("No element {} in {}".format(exc, list(children_map)),)
            raise

        if value is not None:
            xs_boolean = ("boolean", "http://www.w3.org/2001/XMLSchema")
            has_boolean_restriction = False
            typ = client.wsdl.schema.types.get(element.type)
            if isinstance(typ, suds.xsd.sxbasic.Simple):
                for child in typ.rawchildren:
                    if (
                        isinstance(child, suds.xsd.sxbasic.Restriction)
                        and child.ref == xs_boolean
                    ):
                        has_boolean_restriction = True
                        break
            if element.type == xs_boolean or has_boolean_restriction:
                value = "true" if value else "false"
            setattr(instance, element_name, value)
            has_value = True
        elif element.min == "0":
            if hasattr(instance, element_name):
                # factory created some default subelement (e.g. xsd:enum) but
                # enedis web-service doesn't like those empty tags
                delattr(instance, element_name)
        else:
            raise ValueError("Expecting a value for {}".format(option))

    if has_value:
        return instance
    return None


def get_option(args: Union[dict[str, Any], argparse.Namespace], option: str) -> Any:
    if isinstance(args, dict):
        return args.get(option, None)
    else:
        return getattr(args, option)


def build_xstypes_map(
    client: Client,
) -> dict[str, tuple[suds.xsd.sxbase.SchemaObject, str]]:
    """Return a dictionary of type names defined in the XML schema (without
    namespace nor prefix), associated to 2-uple `(type object, prefix)`.

    """
    assert len(client.sd) == 1, "More than one service: {}".format(client.sd)

    xstypes_map = {}
    service_def = client.sd[0]
    for xstype in service_def.types:
        assert xstype[0] is xstype[1]  # duh?!
        xstype = xstype[0]
        ns = xstype.resolve().namespace()[1]
        prefix = service_def.getprefix(ns)
        # Fix for issue #34
        if service_def.service.name != "CommanderAccesDonneesMesures-V1.0":
            assert xstype.name not in xstypes_map
        xstypes_map[xstype.name] = (xstype, prefix)

    return xstypes_map


def xstype_children_map(
    xstype: suds.xsd.sxbase.SchemaObject,
) -> dict[str, suds.xsd.sxbasic.Element]:
    """Return a dictionary of children tags for xstype, without namespace nor
    prefix.

    """
    children_map = {}
    for element, _ in xstype.children():
        children_map[element.name] = element

    return children_map


def iter_methods(client: Client) -> Iterator[suds.sudsobject.Facade]:
    """Return an iterator on exposerd methods suds instances."""
    for service in client.wsdl.services:
        for port in service.ports:
            for method in port.methods.values():
                yield method


def dict_from_dicts(*dicts: dict[str, Any]) -> dict[str, Any]:
    """Build a dictionary from multiple dictionaries. In case of key conflict, the
    latest one wins.

    """
    result = {}
    for d in dicts:
        result.update(d)

    return result
