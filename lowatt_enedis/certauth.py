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

from http.client import HTTPSConnection
from urllib.request import HTTPSHandler, build_opener

from suds.transport.http import HttpTransport


class _HTTPSClientAuthHandler(HTTPSHandler):
    def __init__(self, cert_file, key_file):
        super().__init__()
        self.cert_file = cert_file
        self.key_file = key_file

    def https_open(self, req):
        return self.do_open(self.get_connection, req)

    def get_connection(self, host, timeout=300):
        return HTTPSConnection(
            host,
            key_file=self.key_file,
            cert_file=self.cert_file,
        )


class HTTPSClientCertTransport(HttpTransport):
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

    def __init__(self, cert_file, key_file, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_open = build_opener(
            _HTTPSClientAuthHandler(cert_file, key_file),
        ).open

    def u2open(self, u2request):
        """Open an return a connection.

        :param u2request: A urllib2 request.
        :return: The opened file-like urllib2 object.
        """
        return self.url_open(u2request, timeout=self.options.timeout)
