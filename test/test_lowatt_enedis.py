import argparse
import datetime
import os

import suds.sudsobject
from suds.client import Client, SoapClient

import lowatt_enedis as le
import lowatt_enedis.services  # noqa: register services


def dummy_args() -> argparse.Namespace:
    return argparse.Namespace(
        cert_file=None, key_file=None, login="bob", homologation=False, output="json"
    )


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
        client: Client,
        args: argparse.Namespace,  # noqa: ARG001
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

    le.handle_cli_command("testws", dummy_args())
    assert handler_called
    assert service_location == (b"https://sge-ws.enedis.fr/RecherchePoint/v2.0")

    handler_called = False
    service_location = None
    # XXX dummy_args(homologation=True) didn't work as expected
    cli_args = dummy_args()
    cli_args.homologation = True
    le.handle_cli_command("testws", cli_args)
    assert handler_called
    assert service_location == (
        b"https://sge-homologation-ws.enedis.fr/RecherchePoint/v2.0"
    )


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
            datetime.datetime(2020, 2, 29, 23, tzinfo=datetime.timezone.utc),
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
