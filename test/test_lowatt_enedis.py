import argparse
import contextlib
import datetime
import io
import os
import sys
from typing import Iterator
from unittest import mock

import pkg_resources
import pytest
import suds.sudsobject
from suds import WebFault
from suds.client import Client, SoapClient

import lowatt_enedis as le
import lowatt_enedis.services  # noqa: register services
from lowatt_enedis.__main__ import run


def args() -> argparse.Namespace:
    return argparse.Namespace(
        cert_file=None, key_file=None, login="bob", homologation=False, output="json"
    )


@contextlib.contextmanager
def override_sys_argv(argv: list[str]) -> Iterator[None]:
    old, sys.argv = sys.argv, argv
    try:
        yield
    finally:
        sys.argv = old


def test_introspection() -> None:
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


def test_ws_decorator() -> None:
    service, options, handler = le.COMMAND_SERVICE["search"]
    service_location = None
    handler_called = False

    @le.register("testws", service, options)
    @le.ws(service)
    def test_handler(
        client: Client, args: argparse.Namespace
    ) -> suds.sudsobject.Object:
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
        return suds.sudsobject.Object()

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


def test_cli_output(capsys: pytest.CaptureFixture[str]) -> None:
    @le.register(
        "test",
        "RecherchePoint-v2.0",
        {
            "--do-raise": {"action": "store_true", "help": "raise a webfault"},
            "--do-raise-no-value": {
                "action": "store_true",
                "help": "raise a webfault with no value",
            },
        },
    )
    @le.ws("Test-v1.0")
    def handler(client: Client, args: argparse.Namespace) -> suds.sudsobject.Object:
        if args.do_raise:
            fault = suds.sudsobject.Object()
            fault.detail = suds.sudsobject.Object()
            fault.detail.erreur = suds.sudsobject.Object()
            fault.detail.erreur.resultat = suds.sudsobject.Object()
            fault.detail.erreur.resultat._code = "STG42"
            fault.detail.erreur.resultat.value = "some error"
            obj = suds.sax.document.Document(suds.sax.element.Element("error"))
            raise WebFault(fault=fault, document=obj)
        if args.do_raise_no_value:
            # Error as returned by M023 on homologation 23.4
            fault = suds.sudsobject.Object()
            fault.faultcode = "soap:Server"
            fault.faultstring = "Erreur Technique MFI"
            fault.detail = suds.sudsobject.Object()
            fault.detail.erreur = suds.sudsobject.Object()
            fault.detail.erreur.resultat = suds.sudsobject.Object()
            fault.detail.erreur.resultat._code = ""
            obj = suds.sudsobject.Object()
            raise WebFault(fault=fault, document=obj)
        if args.output == "xml":
            # mimic client.options.retxml = True
            return b"<data>foo</data>"
        assert args.output == "json", args
        obj = suds.sudsobject.Object()
        obj.data = "foo"
        return obj

    with mock.patch.dict(
        os.environ,
        {
            "ENEDIS_CERT_FILE": "tls.crt",
            "ENEDIS_KEY_FILE": "tls.key",
            "ENEDIS_LOGIN": "bob",
            "ENEDIS_CONTRAT": "1234",
        },
        clear=True,
    ):
        for cmd, expected_code, expected_out in (
            (
                ["lowatt-enedis", "test"],
                0,
                '<?xml version="1.0" ?>\n<data>foo</data>\n',
            ),
            (
                ["lowatt-enedis", "test", "--do-raise"],
                1,
                '<?xml version="1.0" ?>\n<error/>\n',
            ),
            (["lowatt-enedis", "test", "--output=json"], 0, '{\n  "data": "foo"\n}\n'),
            (
                ["lowatt-enedis", "test", "--do-raise", "--output=json"],
                1,
                '{\n  "errcode": "STG42",\n  "errmsg": "some error"\n}\n',
            ),
            (
                ["lowatt-enedis", "test", "--do-raise-no-value", "--output=json"],
                1,
                '{\n  "errcode": "soap:Server",\n  "errmsg": "Erreur Technique MFI"\n}\n',
            ),
        ):
            with mock.patch.object(sys, "argv", cmd), pytest.raises(SystemExit) as cm:
                run()
            assert cm.value.code == expected_code
            output = capsys.readouterr()
            assert output.out == expected_out
            assert output.err == ""


def test_cli_help() -> None:
    entrypoint = pkg_resources.get_entry_info(
        "lowatt_enedis",
        "console_scripts",
        "lowatt-enedis",
    )
    assert entrypoint is not None
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


def test_detailed_measures_resp2py() -> None:
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


def test_measures_resp2py() -> None:
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


def test_create_from_options_boolean() -> None:
    """Test that create_from_options() outputs valid boolean values.

    suds does not seem to generate/check those values correctly,
    the only valid values for xs:boolean are "true" and "false".
    """

    # From ConsultationMesuresDetaillees-v3.0
    # <xs:complexType name="Demande">
    #     <xs:sequence>
    #         <!-- … -->
    #         <xs:element name="mesuresCorrigees" type="xs:boolean"/>
    #         <!-- … -->
    #     </xs:sequence>
    # </xs:complexType>

    service, _, _ = le.COMMAND_SERVICE["detailsV3"]
    client = Client(le.wsdl(service))
    args = argparse.Namespace()

    for value in [True, False]:
        args.corrigee = value
        option_map = {"corrigee": "mesuresCorrigees"}
        demande = le.create_from_options(client, args, "Demande", option_map)
        assert demande is not None
        assert demande.mesuresCorrigees == ("true" if value else "false")

    # From CommanderTransmissionHistoriqueMesures
    # <xs:simpleType name="BooleenType">
    #     <xs:restriction base="xs:boolean"/>
    # </xs:simpleType>
    # <xs:complexType name="DemandeHistoriqueMesuresType">
    #     <xs:sequence>
    #         <!-- … -->
    #         <xs:element name="mesureCorrigee" type="ds:BooleenType"/>
    #         <!-- … -->
    #     </xs:sequence>
    # </xs:complexType>

    service, _, _ = le.COMMAND_SERVICE["cmdHisto"]
    client = Client(le.wsdl(service))
    args = argparse.Namespace()

    for value in [True, False]:
        args.corrigee = value
        option_map = {"corrigee": "mesureCorrigee"}
        demande = le.create_from_options(
            client, args, "DemandeHistoriqueMesuresType", option_map
        )
        assert demande is not None
        assert demande.mesureCorrigee == ("true" if value else "false")
