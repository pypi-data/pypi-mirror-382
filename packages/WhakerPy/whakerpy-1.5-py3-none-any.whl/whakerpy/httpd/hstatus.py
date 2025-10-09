# -*- coding: UTF-8 -*-
"""
:filename: whakerpy.httpd.hstatus.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: The HTTPD status codes.

.. _This file was initially part of SPPAS: https://sppas.org/
.. _This file is now part of WhakerPy: https://whakerpy.sourceforge.io
..
    -------------------------------------------------------------------------

    Copyright (C) 2023-2024 Brigitte Bigi, CNRS
    Laboratoire Parole et Langage, Aix-en-Provence, France

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

    This banner notice must not be removed.

    -------------------------------------------------------------------------

"""

from __future__ import annotations
from whakerpy.messages import error
from whakerpy.htmlmaker import HTMLTreeError

# -----------------------------------------------------------------------


class HTTPDValueError(ValueError):
    """:ERROR 0377:.

    Invalid HTTPD status code value '{!s:s}'.

    """

    def __init__(self, value):
        self._status = 377
        self.parameter = error(self._status) + (error(self._status)).format(value)

    def __str__(self):
        return repr(self.parameter)

    def get_status(self):
        return self._status

    status = property(get_status, None)

# ---------------------------------------------------------------------------


class HTTPDStatus(object):
    """A status code value of an HTTPD server.

    HTTPD status codes are issued by a server in response to a client's
    request made to the server. All HTTP response status codes are
    separated into five classes or categories. The first digit of the
    status code defines the class of response, while the last two digits
    do not have any classifying or categorization role. There are five
    classes defined by the standard:

        - 1xx informational response – the request was received, continuing process
        - 2xx successful – the request was successfully received, understood, and accepted
        - 3xx redirection – further action needs to be taken in order to complete the request
        - 4xx client error – the request contains bad syntax or cannot be fulfilled
        - 5xx server error – the server failed to fulfil an apparently valid request

    """

    # The full list of standard status codes.
    # https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
    HTTPD_STATUS = {
        100: "Continue",
        101: "Switching Protocols",
        # 102: "Processing", not standard!
        103: "Early Hints",
        200: "OK",
        201: "Created",
        202: "Accepted",
        203: "Non-Authoritative Information",
        204: "No Content",
        205: "Reset Content",
        206: "Partial Content",
        207: "Multi-Status",
        208: "Already Reported",
        226: "IM Used",
        300: "Multiple Choices",
        301: "Moved Permanently",
        302: "Found",
        303: "See Other",
        304: "Not Modified",
        305: "Use Proxy",
        306: "Switch Proxy",
        307: "Temporary Redirect",
        308: "Permanent Redirect",
        400: "Bad Request",
        401: "Unauthorized",
        402: "Payment Required",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        406: "Not Acceptable",
        407: "Proxy Authentication Required",
        408: "Request Timeout",
        409: "Conflict",
        410: "Gone",
        411: "Length Required",
        412: "Precondition Failed",
        413: "Payload Too Large",
        414: "URI Too Long",
        415: "Unsupported Media Type",
        416: "Range Not Satisfiable",
        417: "Expectation Failed",
        418: "I'm a teapot",        # My favorite: https://en.wikipedia.org/wiki/HTTP_418
        421: "Misdirected Request",
        422: "Unprocessable Entity",
        423: "Locked",
        424: "Failed Dependency",
        425: "Too Early",
        426: "Upgrade Required",
        428: "Precondition Required",
        429: "Too Many Requests",
        431: "Request Header Fields Too Large",
        451: "Unavailable For Legal Reasons",
        500: "Internal Server Error",
        501: "Not Implemented",
        502: "Bad Gateway",
        503: "Service Unavailable",
        504: "Gateway Timeout",
        505: "HTTP Version Not Supported",
        506: "Variant Also Negotiates",
        507: "Insufficient Storage",
        508: "Loop Detected",
        510: "Not Extended",
        511: "Network Authentication Required"
    }

    # -----------------------------------------------------------------------

    @staticmethod
    def check(value):
        """Raise an exception if given status value is invalid.

        :param value: (int) A response status.
        :raises: sppasHTTPDValueError
        :return: (int) value

        """
        try:
            value = int(value)
        except ValueError:
            raise HTTPDValueError(value)

        if value not in HTTPDStatus.HTTPD_STATUS.keys():
            raise HTTPDValueError(value)

        return value

    # -----------------------------------------------------------------------

    def __init__(self, code: int = 200):
        """Create the private member for the status code.

        Default status code is 200 for an "OK" httpd response.

        """
        self.__scode = self.check(code)

    # -----------------------------------------------------------------------

    def get(self):
        """Return the status code value (int)."""
        return self.__scode

    def set(self, value):
        """Set a new value to the status code.

        :param value: (int) HTTPD status code value.
        :raises: sppasHTTPDValueError

        """
        value = self.check(value)
        self.__scode = value

    code = property(get, set)

    # -----------------------------------------------------------------------

    def to_html(self, encode: bool = False, msg_error: str = None) -> HTMLTreeError | bytes:
        """Create an error HTML page for the instance of status error and return the tree instance (or serialize).

        :param encode: (bool) Optional, False by default, Boolean to know if we serialize the return or not
        :param msg_error: (str) Optional, an error message for more information for the user

        :return: (HTMLTreeError | bytes) the tree error generated, encoded in bytes for response or object instance

        """
        tree = HTMLTreeError(self, msg_error)

        if encode is True:
            return tree.serialize().encode("utf-8")
        else:
            return tree

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __str__(self):
        return str(self.__scode)

    # -----------------------------------------------------------------------

    def __repr__(self):
        return "{:d} {:s}".format(self.__scode, HTTPDStatus.HTTPD_STATUS[self.__scode])

    # -----------------------------------------------------------------------

    def __eq__(self, other):
        return self.__scode == other
