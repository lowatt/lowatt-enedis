import argparse
import contextlib
import io
import os
import sys
import unittest.mock
from collections.abc import Iterator

import importlib_metadata
import pytest
import suds.sudsobject
from suds import WebFault
from suds.client import Client

import lowatt_enedis as le
import lowatt_enedis.services  # noqa: register services
from lowatt_enedis.__main__ import run


@contextlib.contextmanager
def override_sys_argv(argv: list[str]) -> Iterator[None]:
    old, sys.argv = sys.argv, argv
    try:
        yield
    finally:
        sys.argv = old


def test_cli_help() -> None:
    (entrypoint,) = importlib_metadata.entry_points(
        group="console_scripts",
        name="lowatt-enedis",
    )
    assert entrypoint
    func = entrypoint.load()
    stdout = io.StringIO()
    with (
        pytest.raises(SystemExit) as cm,
        override_sys_argv(
            ["lowatt-enedis", "--help"],
        ),
        contextlib.redirect_stdout(stdout),
    ):
        func()
    assert cm.value.code == 0
    output = stdout.getvalue()
    assert output.startswith("usage: ")


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
    def handler(_client: Client, args: argparse.Namespace) -> suds.sudsobject.Object:
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

    with unittest.mock.patch.dict(
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
            with (
                unittest.mock.patch.object(sys, "argv", cmd),
                pytest.raises(SystemExit) as cm,
            ):
                run()
            assert cm.value.code == expected_code
            output = capsys.readouterr()
            assert output.out == expected_out
            assert output.err == ""
