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

from functools import wraps
import logging
from pathlib import Path, PurePath

from suds import WebFault
from suds.client import Client
from suds.plugin import DocumentPlugin, MessagePlugin

from .certauth import HTTPSClientCertTransport

logging.basicConfig(level=logging.INFO)
# logging.getLogger('suds.client').setLevel(logging.DEBUG)
# logging.getLogger('suds.resolver').setLevel(logging.DEBUG)
# logging.getLogger('suds.mx').setLevel(logging.DEBUG)
# logging.getLogger('suds.transport').setLevel(logging.DEBUG)


WSDL_DIR = PurePath(__file__).parent.joinpath("wsdl")
SERVICES = {x.stem: x.resolve().as_uri() for x in Path(WSDL_DIR).glob("**/*.wsdl")}
COMMAND_SERVICE = {}


def wsdl(service_name):
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


def init_cli(subparsers):
    """Init CLI subparsers according to registered services."""
    for command, (service, options, _) in COMMAND_SERVICE.items():
        subparser = subparsers.add_parser(
            command,
            help='Query the "{}" web-service.'.format(service),
        )
        subparser.add_argument(
            "login",
            help="User login.",
        )
        for option_name, option_kwargs in options.items():
            subparser.add_argument(option_name, **option_kwargs)

        subparser.add_argument(
            "--cert-file",
            default="fullchain.pem",
            help="Client certificate file.",
        )
        subparser.add_argument(
            "--key-file",
            default="privkey.pem",
            help="Client private key file.",
        )
        subparser.add_argument(
            "--homologation",
            default=False,
            action="store_true",
            help="Change service host to use homologation sandbox.",
        )
        subparser.add_argument(
            "--dump",
            action="store_true",
            help="Dump XML response into /tmp/enedis-response.xml.",
        )


def handle_cli_command(command, args):
    """Run `command` service using configuration in `args`."""
    service, _, handler = COMMAND_SERVICE[command]
    client = get_client(
        service,
        args.cert_file,
        args.key_file,
        args.homologation,
        args.dump,
    )
    handler(client, args)


def get_client(service, cert_file, key_file, homologation=False, dump=False):
    # Need custom plugin to handle `xs:choice` potentially expected in service
    # arguments. Non-handling this seems to be an outstanding suds bug, see
    # https://stackoverflow.com/questions/5963404/suds-and-choice-tag
    plugins = [_SetChoicePlugin()]
    if dump:
        plugins.append(StoreXMLResponsePlugin())
    client = Client(
        wsdl(service),
        plugins=plugins,
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


class _SetChoicePlugin(DocumentPlugin):
    def __init__(self):
        self.choosen_tags = {"autorisationClient"}

    def parsed(self, context):
        self._rec_set_choices(context.document)

    def _rec_set_choices(self, document):
        for i in document.children:
            if i.name == "choice":
                for j in i.children:
                    if j.getAttribute("name").value in self.choosen_tags:
                        i.parent.append(j)

            else:
                # recursion
                self._rec_set_choices(i)


def register(command, service, options):
    """Decorator registering function as a service handler for CLI `command`,
    matching `service` web-service name, accepting `options` (list of dict given
    to `argparse.ArgumentParser.add_argument`)

    """

    def decorator(func):
        COMMAND_SERVICE[command] = (service, options, func)
        return func

    return decorator


class WSException(Exception):
    pass


def ws(service, header_ns_prefix="ns4"):
    """Decorator around sge web service call, returning a wrapper that properly set
    SOAP headers required by the service

    """

    def decorator(func):
        service_version = service.split("-")[1][1:]

        @wraps(func)
        def call_service(client, args):
            client.xstypes_map = build_xstypes_map(client)
            header = client.factory.create("{}:entete".format(header_ns_prefix))
            header.version = service_version
            header.infoDemandeur = client.factory.create(
                "{}:infoDemandeur".format(header_ns_prefix),
            )
            header.infoDemandeur.loginDemandeur = get_option(args, "login")
            client.set_options(soapheaders=header)

            try:
                return func(client, args)
            except WebFault as exc:
                res = exc.fault.detail.erreur.resultat
                raise WSException("{}: {}".format(res._code, res.value))

        return call_service

    return decorator


def create_from_options(client, args, xstype_name, options_map):
    """Create and return an `xstype_name` element, and fill it according to
    `options_map` {arg name: xs element name}` mapping by looking for value in
    command line `args`.

    """
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
            if element.type[0] == "BooleenType":
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


def get_option(args, option):
    if isinstance(args, dict):
        return args.get(option, None)
    else:
        return getattr(args, option)


def build_xstypes_map(client):
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
        assert xstype.name not in xstypes_map
        xstypes_map[xstype.name] = (xstype, prefix)

    return xstypes_map


def xstype_children_map(xstype):
    """Return a dictionary of children tags for xstype, without namespace nor
    prefix.

    """
    children_map = {}
    for element, _ in xstype.children():
        children_map[element.name] = element

    return children_map


def iter_methods(client):
    """Return an iterator on exposerd methods suds instances."""
    for service in client.wsdl.services:
        for port in service.ports:
            for method in port.methods.values():
                yield method


def dict_from_dicts(*dicts):
    """Build a dictionary from multiple dictionaries. In case of key conflict, the
    latest one wins.

    """
    result = {}
    for d in dicts:
        result.update(d)

    return result


class StoreXMLResponsePlugin(MessagePlugin):
    def received(self, context):
        with open("/tmp/enedis-response.xml", "wb") as stream:
            stream.write(context.reply)
