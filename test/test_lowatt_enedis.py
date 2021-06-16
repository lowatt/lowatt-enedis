import contextlib
from dataclasses import dataclass
import datetime
import io
import os
import pkg_resources
import sys

import pytest
from suds.client import Client, SoapClient

import lowatt_enedis as le
import lowatt_enedis.services  # noqa: register services


@dataclass(init=True)
class args:
    cert_file = None
    key_file = None
    login = "bob"
    homologation = False
    dump = False


@contextlib.contextmanager
def override_sys_argv(argv):
    old, sys.argv = sys.argv, argv
    try:
        yield
    finally:
        sys.argv = old


def test_introspection():
    service = "RecherchePoint-v2.0"
    service_wsdl = le.wsdl(service)
    assert service_wsdl.endswith(".wsdl")

    client = Client(service_wsdl)
    xstype_map = le.build_xstypes_map(client)
    assert "CriteresType" in xstype_map

    xstype, prefix = xstype_map["CriteresType"]
    assert prefix == "ns3"

    children_map = le.xstype_children_map(xstype)
    assert "numSiret" in children_map
    assert children_map["numSiret"].min == "0"


def test_ws_decorator():
    service, options, handler = le.COMMAND_SERVICE["search"]

    @le.register("testws", service, options)
    @le.ws(service)
    def test_handler(client, args):
        nonlocal handler_called, service_location

        handler_called = True

        assert client.options.location is None

        headers = client.options.soapheaders
        assert headers.version == "2.0"
        assert headers.infoDemandeur.loginDemandeur == "bob"

        for service in client.wsdl.services:
            for port in service.ports:
                for method in port.methods.values():
                    assert service_location is None
                    service_location = method.location

    handler_called = False
    service_location = None
    le.handle_cli_command("testws", args())
    assert handler_called
    assert service_location == (b"https://sge-b2b.enedis.fr/RecherchePoint/v2.0")

    handler_called = False
    service_location = None
    # XXX args(homologation=True) didn't work as expected
    _args = args()
    _args.homologation = True
    le.handle_cli_command("testws", _args)
    assert handler_called
    assert service_location == (
        b"https://sge-homologation-b2b.enedis.fr/RecherchePoint/v2.0"
    )


def test_cli_help():
    entrypoint = pkg_resources.get_entry_info(
        "lowatt_enedis",
        "console_scripts",
        "lowatt-enedis",
    )
    func = entrypoint.load()
    stdout = io.StringIO()
    with pytest.raises(SystemExit) as cm, override_sys_argv(
        ["lowatt-enedis", "--help"],
    ), contextlib.redirect_stdout(stdout):
        func()
    assert cm.value.code == 0
    output = stdout.getvalue()
    assert output.startswith("usage: ")


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def test_detailed_measures_resp2py():
    service, options, handler = le.COMMAND_SERVICE["details"]
    client = Client(le.wsdl(service))
    soap = SoapClient(client, client.service.consulterMesuresDetaillees.method)
    resp_file = os.path.join(DATA_DIR, "consulterMesuresDetailleesResponse.xml")
    with open(resp_file) as stream:
        resp = soap.succeeded(soap.method.binding.input, stream.read())
        data = list(le.services.detailed_measures_resp2py(resp))
        assert len(data) == 8
        assert data[0] == (
            datetime.datetime(2020, 2, 29, 23, tzinfo=le.services.UTC),
            100,
        )


def test_measures_resp2py():
    service, options, handler = le.COMMAND_SERVICE["measures"]
    client = Client(le.wsdl(service))
    soap = SoapClient(client, client.service.consulterMesures.method)
    resp_file = os.path.join(DATA_DIR, "consulterMesuresResponse.xml")
    with open(resp_file) as stream:
        resp = soap.succeeded(soap.method.binding.input, stream.read())
        data = list(le.services.measures_resp2py(resp))
        assert data == [
            {
                "calendrier": "DI000001",
                "classeTemporelle": "BASE",
                "grandeurPhysique": "EA",
                "grille": "turpe",
                "mesures": [
                    (
                        datetime.date(2021, 2, 3),
                        datetime.date(2021, 3, 5),
                        483,
                        "REEL",
                        "CYCLIQUE",
                        "INITIALE",
                    ),
                    (
                        datetime.date(2021, 1, 5),
                        datetime.date(2021, 2, 3),
                        494,
                        "REEL",
                        "CYCLIQUE",
                        "INITIALE",
                    ),
                ],
                "unit": "kWh",
            },
            {
                "calendrier": "FC000013",
                "classeTemporelle": "BASE",
                "grandeurPhysique": "EA",
                "grille": "frn",
                "mesures": [
                    (
                        datetime.date(2021, 2, 3),
                        datetime.date(2021, 3, 5),
                        483,
                        "REEL",
                        "CYCLIQUE",
                        "INITIALE",
                    ),
                    (
                        datetime.date(2021, 1, 5),
                        datetime.date(2021, 2, 3),
                        494,
                        "REEL",
                        "CYCLIQUE",
                        "INITIALE",
                    ),
                ],
                "unit": "kWh",
            },
        ]
