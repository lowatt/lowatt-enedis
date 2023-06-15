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
`lowatt_enedis.certauth`
------------------------

Provide a SUDS_ transport class to connect through an HTTPS connection using
a client SSL certificate.

.. autoclass:: HTTPSClientCertTransport

.. _SUDS: https://suds-py3.readthedocs.io/en/latest

"""

import ssl
from http.client import HTTPResponse, HTTPSConnection
from typing import Any
from urllib.request import HTTPSHandler, Request, build_opener

import certifi
from suds.transport.http import HttpTransport


class _HTTPSClientAuthHandler(HTTPSHandler):
    def __init__(self, cert_file: str, key_file: str):
        super().__init__()
        self.cert_file = cert_file
        self.key_file = key_file

    def https_open(self, req: Request) -> HTTPResponse:
        return self.do_open(self.get_connection, req)  # type: ignore[arg-type]

    def get_connection(self, host: str, timeout: int = 300) -> HTTPSConnection:
        context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_CLIENT)
        context.load_cert_chain(self.cert_file, self.key_file)
        context.load_verify_locations(cafile=certifi.where())
        return HTTPSConnection(host, context=context)


class HTTPSClientCertTransport(HttpTransport):  # type: ignore[misc]
    """SUDS_ transport class to connect through an HTTPS connection using
    a client SSL certificate.

    :param cert_file: path to the full-chain certificate file.
    :param key_file: path to the private key file.

    Usage ::

        from suds.client import Client
        client = Client(
            service_url,
            transport=HTTPSClientCertTransport(cert_file, key_file),
        )

    .. _SUDS: https://suds-py3.readthedocs.io/en/latest
    """

    def __init__(self, cert_file: str, key_file: str, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.url_open = build_opener(
            _HTTPSClientAuthHandler(cert_file, key_file),
        ).open

    def u2open(self, u2request: Request) -> HTTPResponse:
        """Open an return a connection.

        :param u2request: A urllib2 request.
        :return: The opened file-like urllib2 object.
        """
        return self.url_open(u2request, timeout=self.options.timeout)  # type: ignore[no-any-return]
