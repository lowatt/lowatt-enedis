import contextlib
import doctest
import importlib
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Iterator, TypedDict
from unittest.mock import patch

import freezegun
import lxml.doctestcompare
import lxml.etree
import lxml.objectify
import pkg_resources
import pytest
import yaml

import lowatt_enedis.services


def get_cases(_cache: dict[None, dict[str, str]] = {}) -> dict[str, str]:
    with contextlib.suppress(KeyError):
        return _cache[None]
    cases: dict[str, str] = {}
    with (Path(__file__).parent.parent / "doc" / "homologation.md").open() as f:
        for line in f:
            match = re.search(r"\|(.*)\|.*`(lowatt-enedis .*)`.*$", line)
            if match:
                case, command = match.groups()
                case = case.strip()
                assert case not in cases
                cases[case] = command
    assert len(cases) == 72
    _cache[None] = cases
    return cases


class ExpectedDict(TypedDict):
    url: str
    data: str


EXPECTED_FILENAME = Path(__file__).parent / "data" / "requests.yaml"


def get_expected(
    _cache: dict[None, dict[str, ExpectedDict]] = {}
) -> dict[str, ExpectedDict]:
    with contextlib.suppress(KeyError):
        return _cache[None]
    with EXPECTED_FILENAME.open() as f:
        result = _cache[None] = yaml.safe_load(f)
    return result  # type: ignore[no-any-return]


class Dumper(yaml.SafeDumper):
    pass


def multiline_dump(dumper: yaml.SafeDumper, data: str) -> yaml.ScalarNode:
    if len(data.splitlines()) > 1:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


Dumper.add_representer(str, multiline_dump)


def set_expected(case: str, expected: ExpectedDict) -> None:
    try:
        with EXPECTED_FILENAME.open() as f:
            result = yaml.safe_load(f)
    except FileNotFoundError:
        result = {}

    result[case] = expected

    with EXPECTED_FILENAME.open("w") as f:
        yaml.dump(result, f, allow_unicode=True, sort_keys=True, Dumper=Dumper)


@contextlib.contextmanager
def override_sys_argv(argv: list[str]) -> Iterator[None]:
    old, sys.argv = sys.argv, argv
    try:
        yield
    finally:
        sys.argv = old


@pytest.fixture(scope="session")
def certs(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path]:
    certs = tmp_path_factory.mktemp("certs")
    certfile, keyfile = certs / "cert.pem", certs / "key.pem"
    subprocess.check_call(
        [
            "openssl",
            "req",
            "-x509",
            "-newkey",
            "rsa:2048",
            "-nodes",
            "-keyout",
            str(keyfile),
            "-out",
            str(certfile),
            "-batch",
        ],
    )
    return certfile, keyfile


def assert_xml_equal(actual: str, expected: str) -> None:
    checker = lxml.doctestcompare.LXMLOutputChecker()
    if not checker.check_output(actual, expected, 0):
        message = checker.output_difference(doctest.Example("", expected), actual, 0)
        raise AssertionError(message)


@pytest.mark.parametrize("case", list(get_cases()))
def test_requests(
    case: str, tmp_path: Path, certs: tuple[Path, Path], regen_test_data: bool
) -> None:
    # fix some defaults set at import time
    with freezegun.freeze_time("2022-02-22"), patch.dict(
        "os.environ", {"ENEDIS_CONTRAT": "1234"}
    ):
        importlib.reload(lowatt_enedis.services)
    entrypoint = pkg_resources.get_entry_info(
        "lowatt_enedis",
        "console_scripts",
        "lowatt-enedis",
    )
    assert entrypoint
    func = entrypoint.load()
    command = shlex.split(get_cases()[case])

    with override_sys_argv(command), patch.dict(
        "os.environ",
        {
            "ENEDIS_LOGIN": "test@example.com",
            "ENEDIS_CERT_FILE": str(certs[0]),
            "ENEDIS_KEY_FILE": str(certs[1]),
            "ENEDIS_HOMOLOGATION": "true",
        },
    ), patch("lowatt_enedis.certauth._HTTPSClientAuthHandler.https_open") as client:

        class FakeResponse:
            code = 500
            msg = b""

            def info(self) -> dict[str, str]:
                return {}

            def read(self) -> bytes:
                return (
                    b'<?xml version="1.0" ?>'
                    b'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">'
                    b'<soap:Body xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">'
                    b'<ns3:Fault xmlns:ns3="http://schemas.xmlsoap.org/soap/envelope/">'
                    b"</ns3:Fault>"
                    b"</soap:Body>"
                    b"</soapenv:Envelope>"
                )

            def close(self) -> None:
                pass

        resp = FakeResponse()
        client.return_value = resp
        with pytest.raises(SystemExit) as cm:
            func()
        assert cm.value.code == 1
    if sys.version_info[:2] <= (3, 7):
        req = list(client.mock_calls[0])[1][0]
    else:
        req = client.mock_calls[0].args[0]
    data = lxml.etree.tostring(
        lxml.objectify.fromstring(req.data), encoding="utf8", pretty_print=True
    ).decode()
    actual: ExpectedDict = {"url": req.full_url, "data": data}
    if regen_test_data:
        set_expected(case, actual)
    else:
        expected = get_expected()[case]
        assert actual["url"] == expected["url"]
        assert_xml_equal(actual["data"], expected["data"])
