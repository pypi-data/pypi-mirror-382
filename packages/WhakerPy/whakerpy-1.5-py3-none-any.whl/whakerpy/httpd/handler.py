# -*- coding: UTF-8 -*-
"""
:filename: whakerpy.httpd.handler.py
:author:  Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: Manage an HTTPD handler for any web-based application.

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
import logging
import types
import http.server
import os.path

from .hstatus import HTTPDStatus
from .hutils import HTTPDHandlerUtils

# ---------------------------------------------------------------------------


class HTTPDHandler(http.server.BaseHTTPRequestHandler):
    """Web-based application HTTPD handler.

    This class is used to handle the HTTP requests that arrive at the server.

    This class is instantiated by the server each time a request is received
    and then a response is created. This is an HTTPD handler for any Web-based
    application server. It parses the request and the headers, then call a
    specific method depending on the request type.

    In this handler, HTML pages are supposed to not be static. Instead,
    they are serialized from an HTMLTree instance -- so not read from disk.
    The server contains the page's bakery, the handler is then asking the
    server page's bakery to get the html content and response status.

    The parent server is supposed to have all the pages as members in a
    dictionary, i.e. it's a sppasBaseHTTPDServer. Each page has a bakery
    to create the response content. However, this handler can also be used
    with any other http.server.ThreadingHTTPServer.

    The currently supported HTTPD responses status are:

        - 200: OK
        - 205: Reset Content
        - 403: Forbidden
        - 404: Not Found
        - 410: Gone
        - 418: I'm not a teapot

    """

    def get_default_page(self, default: str = "index.html") -> str:
        """Retrieve the server default page name.

        This method first checks if the server has a callable 'default' method
        to determine the default page name. If not, it falls back to the
        provided default value.

        :param default: (str) The fallback default page name, if no server-specific
                               method is found. Defaults to "index.html".
        :return: (str) The name of the default page.

        """
        # Check if the server has a callable 'default' method.
        if hasattr(self.server, 'default') and callable(self.server.default):
            return self.server.default()

        # Fallback to the provided default page name.
        return default

    # -----------------------------------------------------------------------

    def _set_headers(self, status: int, mime_type: str = None) -> None:
        """Set the HTTPD response headers.

        :param status: (int) A response status.
        :param mime_type: (str) The mime type of the file response
        :raises: sppasHTTPDValueError

        """
        status = HTTPDStatus.check(status)
        self.send_response(status)

        if mime_type is not None:
            self.send_header('Content-Type', mime_type)

        self.end_headers()

    # -----------------------------------------------------------------------

    def _response(self, content, status: int, mime_type: str = None) -> None:
        """Make the appropriate HTTPD response.

        :param content: (bytes|iterator) The HTML response content or an iterator
                        yielding chunks of bytes.
        :param status: (int) The HTTPD status code of the response.
        :param mime_type: (str) The mime type of the file response.

        """
        self._set_headers(status, mime_type)

        if isinstance(content, types.GeneratorType) is True:
            # Write one chunk at a time
            for chunk in content:
                self.wfile.write(chunk)
        else:
            # Write the whole bytes content in once
            self.wfile.write(content)

        # Shutdown the server if status is 410.
        if status == 410:
            self.server.shutdown()

    # -----------------------------------------------------------------------

    def _bakery(self, handler_utils: HTTPDHandlerUtils, events: dict, mime_type: str) -> tuple:
        """Process the events and return the html page content or json data and status.

        :param handler_utils: (HTTPDhandlerUtils)
        :param events: (dict) key=event name, value=event value
        :param mime_type: (str) The mime type of the file response
        :return: tuple(bytes, HTTPDStatus) the content of the response the httpd status

        """
        # The server is not the custom one for a WhakerPy application.
        if hasattr(self.server, 'page_bakery') is False:
            return handler_utils.static_content(self.path[1:])

        # Get the response from any WhakerPy Bakery system
        content, status = self.server.page_bakery(handler_utils.get_page_name(), self.headers, events,
                                                  handler_utils.has_to_return_data(mime_type))
        return content, status

    # -----------------------------------------------------------------------
    # Override BaseHTTPRequestHandler classes.
    # -----------------------------------------------------------------------

    def do_HEAD(self) -> None:
        """Prepare the response to a HEAD request.

        """
        logging.debug("HEAD -- requested: {}".format(self.path))
        self._set_headers(200)

    # -----------------------------------------------------------------------

    def do_GET(self) -> None:
        """Prepare the response to a GET request.

        """
        logging.debug(" ---- DO GET -- requested: {}".format(self.path))

        handler_utils = HTTPDHandlerUtils(self.headers, self.path, self.get_default_page())
        self.path = handler_utils.get_path()
        mime_type = HTTPDHandlerUtils.get_mime_type(self.path)

        # The client requested a static file.
        # (must be done before checking mime type in case the client ask a html static file)
        if os.path.exists(handler_utils.get_path()) or os.path.exists(handler_utils.get_path()[1:]):
            content, status = handler_utils.static_content(self.path[1:])
        # The client requested an HTML page. Response content is created by the server.
        elif mime_type == "text/html":
            content, status = self._bakery(handler_utils, dict(), mime_type)
        else:
            # Unknown: try to get a static file
            content, status = handler_utils.static_content(self.path[1:])

        # WhakerPy 1.1: content can be either ['bytes'] or iterator, depending
        # on the requested file size
        self._response(content, status.code, mime_type)

    # -----------------------------------------------------------------------

    def do_POST(self) -> None:
        """Prepare the response to a POST request.

        """
        logging.debug(" ----- DO POST -- requested: {}".format(self.path))

        handler_utils = HTTPDHandlerUtils(self.headers, self.path, self.get_default_page())
        self.path = handler_utils.get_path()

        events, accept = handler_utils.process_post(self.rfile)
        content, status = self._bakery(handler_utils, events, accept)

        # WhakerPy 1.1: content can be either ['bytes'] or iterator, depending
        # on the requested file size
        self._response(content, status.code, accept)

    # -----------------------------------------------------------------------

    def log_request(self, code='-', size='-') -> None:
        """Override. For a quiet handler pls!!!."""
        pass

