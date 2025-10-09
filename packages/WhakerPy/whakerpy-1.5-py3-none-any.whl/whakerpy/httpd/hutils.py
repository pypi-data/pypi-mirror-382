# -*- coding: UTF-8 -*-
"""
:filename: whakerpy.httpd.hutils.py
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: Class to help to manage http request for httpd or wsgi application.

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
import os
import json
import codecs
import logging
import mimetypes
import types
from io import BufferedReader

from http.client import HTTPMessage
from urllib.parse import parse_qsl
from urllib.parse import unquote

from .hstatus import HTTPDStatus
from .permissions import UnixPermissions
from .permissions import FileAccessChecker

# -----------------------------------------------------------------------


class HTTPDHandlerUtils:

    def __init__(self, headers: HTTPMessage | dict, path: str, default_page: str = "index.html"):
        """Instantiate class, filter the path for getters method and get the headers data

        :param headers: (HTTPMessage|dict) the headers of the request
        :param path: (str) the brut path get by the request
        :param default_page: (str) optional parameter, default page when the page doesn't specify it

        """
        self.__path, self.__page_name = HTTPDHandlerUtils.filter_path(path, default_page)
        self.__headers = dict()

        if isinstance(headers, HTTPMessage) is True or isinstance(headers, dict) is True:
            self.__headers = headers
        else:
            raise TypeError("The headers parameter has to be a dictionary or HTTPMessage class!")

    # -----------------------------------------------------------------------
    # GETTERS
    # -----------------------------------------------------------------------

    def get_path(self) -> str:
        """Get the path of the request after filtered true path in constructor.

        :return: (str) the path

        """
        return self.__path

    # -----------------------------------------------------------------------

    def get_page_name(self) -> str:
        """Get the name of the page after filtered path in constructor.

        :return: (str) the page name ask by the request

        """
        return self.__page_name

    # -----------------------------------------------------------------------
    # PUBLIC METHODS
    # -----------------------------------------------------------------------

    def static_content(self, filepath: str) -> tuple:
        """Return the content of a static file and update the corresponding status.

        This method checks the existence of the file and its permissions before
        returning its content. If the file does not exist or is a directory,
        an appropriate HTTP status and message will be logged.

        :param filepath: (str) The path of the file to return.
        :return: (tuple[bytes|iterator, HTTPDStatus]) A tuple containing the file content
                 in bytes and the corresponding HTTP status.

        """
        # Check if the requested filepath exists
        if os.path.exists(filepath) is False:
            return self.__log_and_status(404, filepath, "File not found")

        # Check if the requested filepath is a directory:
        # Access to directories is forbidden regardless of permissions.
        if os.path.isfile(filepath) is False:
            return self.__log_and_status(403, filepath, "Folder access is not granted")

        # Check if the requested filepath is a directory:
        # Access to directories is forbidden regardless of permissions.
        try:
            p = UnixPermissions()
            checker = FileAccessChecker(filepath)
            if checker.read_allowed(who=f"{p.group}&{p.others}") is False:
                return self.__log_and_status(403, filepath, "Attempted access to non-allowed file")
        except EnvironmentError:
            # Possibly running in a local application (e.g., Windows); no risk.
            # No need for permission checks in this case.
            pass

        # The requested filepath is a regular existing file: check permissions.
        try:
            content = self.__open_file_to_binary(filepath)
            return content, HTTPDStatus(200)   # bytes or iterator
        except Exception as e:
            status = HTTPDStatus(500)
            return status.to_html(encode=True, msg_error=str(e)), status

    # -----------------------------------------------------------------------

    def __log_and_status(self, code: int, filepath: str, msg: str) -> tuple[bytes, HTTPDStatus]:
        """Log the error message and return the corresponding HTTP status.

        This method logs the provided message along with the file path and
        returns an HTML error message with the appropriate HTTP status.

        :param code: (int) The HTTP status code to return.
        :param filepath: (str) The path of the file related to the error.
        :param msg: (str) The message to log regarding the error.
        :return: (tuple[str, HTTPDStatus]) A tuple containing the HTML error
                 message and the corresponding HTTP status.

        """
        status = HTTPDStatus(code)
        logging.error(f"{msg}: {filepath}")
        msg = f"{msg}: {os.path.basename(filepath)}"
        return status.to_html(encode=True, msg_error=msg), status

    # -----------------------------------------------------------------------

    def process_post(self, body: BufferedReader) -> tuple[dict, str]:
        """Process the request body to return events and accept mime type.

        :param body: (BufferedReader) The body buffer of the request (rfile)
        :return: (dict, str) the body and accept mime type

        """
        html_mime = "text/html"
        events = dict()
        accept_type = html_mime

        # Check for wsgi server case
        if self.__headers.get("REQUEST_METHOD", "POST").upper() == "POST":

            # Parse the posted data
            events = self.__extract_body_content(body)

            # Create the response
            accept_type = self.__get_headers_value('Accept', "text/html")
            if html_mime in accept_type:
                accept_type = html_mime
            token = self.__get_headers_value('X-Auth-Token')
            if token is not None:
                events["token"] = token.replace("Bearer ", "")

        return events, accept_type

    # -----------------------------------------------------------------------
    # STATIC METHODS
    # -----------------------------------------------------------------------

    @staticmethod
    def get_mime_type(filename: str) -> str:
        """Return the mime type of given file name or path.

        :param filename: (str) The name or path of the file
        :return: (str) The mime type of the file or 'unknown' if we can't find the type

        """
        mime_type, _ = mimetypes.guess_type(filename)

        if mime_type is None:
            return "unknown"
        else:
            return mime_type

    # -----------------------------------------------------------------------

    @staticmethod
    def filter_path(path: str, default_path: str = "index.html") -> tuple[str, str]:
        """Parse the path to return the correct filename and page name.

        :param path: (str) The path obtain from the request or environ
        :param default_path: (str) The default path to add if the path ends with '/'
        :return: (tuple[str, str]) the requested filename and the requested page name

        """
        # decode html url (for example space character which became %20)
        path = unquote(path)

        # this block has to be before the '/' condition
        # example: http://localhost:8080/?wexa_color=light
        if "?" in path:
            path = path[:path.index("?")]

        if len(path) == 0:
            return f"/{default_path}", default_path

        filepath = path
        page_name = os.path.basename(path)
        _, extension = os.path.splitext(path)

        if len(page_name) == 0 or len(extension) == 0:
            page_name = default_path

            if filepath.endswith("/"):
                filepath += default_path

        return filepath, page_name

    # -----------------------------------------------------------------------

    @staticmethod
    def has_to_return_data(accept_type: str) -> bool:
        """Determine the type of the server return: True for data.

        Determine if the server should return data (e.g., JSON, image, video,
        etc.) instead of an HTML page based on the 'Accept' header's MIME type.

        :param accept_type: (str) The MIME type of the 'Accept' header request
        :return: (bool) True if the server should return data, False if HTML content is expected

        """
        data_types = [
            "application/json",
            "image/",
            "video/",
            "audio/",
            "application/ogg"
        ]
        for d in data_types:
            if accept_type.startswith(d) is True:
                return True
        return False

    # -----------------------------------------------------------------------

    @staticmethod
    def bakery(pages: dict, page_name: str, headers: dict, events: dict, has_to_return_data: bool = False)\
            -> tuple[bytes, HTTPDStatus]:
        """Process received events and bake the given page.

        :param pages: (dict) A dictionary with key=page_name and value=ResponseRecipe
        :param page_name: (str) The current page name
        :param headers: (dict) The headers of the http request
        :param events: (dict) The events extract from the request (only for POST request, send empty dict for GET)
        :param has_to_return_data: (bool) False by default, Boolean to know if we have to return the html page or data
        :return: (tuple[bytes, HTTPDStatus]) The content to answer to the client and the status of the response

        """
        # get the response and check it
        response = pages.get(page_name)

        if response is None:
            status = HTTPDStatus(404)
            return status.to_html(encode=True, msg_error=f"Page not found: {page_name}"), status

        content = bytes(response.bake(events, headers=headers), "utf-8")

        # check if we have to return data or HTML page
        if has_to_return_data is True:
            # get data set by the current page
            content = response.get_data()
            if isinstance(content, (bytes, bytearray)) is False:
                content = bytes(content, "utf-8")
            response.reset_data()

        # get the status of the response
        status = response.status

        if isinstance(status, int):  # if the user makes a mistake and set in the status directly an integer
            status = HTTPDStatus(status)
        elif hasattr(status, 'code') is False:
            raise TypeError(f"The status has to be an instance of HTTPDStatus or int."
                            f"Got {status} instead.")

        return content, status

    # -----------------------------------------------------------------------

    @staticmethod
    def build_default_headers(filepath: str, content=None, browser_cache=False, varnish=False) -> list:
        """Build HTTP response headers for the requested file.

        This method generates the HTTP headers necessary for serving a file,
        including its MIME type and cache-control directives.

        :param filepath: (str) The absolute or relative path to the requested static file.
        :param content: (bytes|iterator|None) The content of the requested file.
        :param browser_cache: (bool) Whether the browser cache is enabled or not.
                        If False, browser caching is explicitly disabled.
        :param varnish: (bool) Indicates whether the server should enable Varnish cache.
                        If False, server caching is explicitly disabled.
        :return: (list) A list of tuples representing the HTTP response headers.

        """
        # Initialize cache-control header with default values to disable caching.
        # no-cache: ensures that users always receive the most up-to-date version of the resource.
        # no-store: prevents the browser (or caching mechanisms) from storing the resource at all.
        # must-revalidate: tells the browser that once the resource becomes stale, it must not
        #                  be used without revalidation with the server.
        cache = list()
        if browser_cache is False:
            cache.append("no-cache")
            cache.append("no-store")
            cache.append("must-revalidate")

        if varnish is False:
            # Add a directive to explicitly set the maximum cache age to zero.
            cache.append("max-age=0")

        # Build the headers list with the MIME type and cache directives.
        headers = [('Content-Type', HTTPDHandlerUtils.get_mime_type(filepath))]
        if len(cache) > 0:
            headers.append(('Cache-Control', ','.join(cache)))
            headers.append(('Pragma', 'no-cache'))
            headers.append(('Expires', '0'))

        # If content is an iterator, calculate the file size and
        # add Content-Length
        if isinstance(content, types.GeneratorType) is True:
            content_length, content = HTTPDHandlerUtils.getsize_from_iterator(content)
            headers.append(('Content-Length', str(content_length)))

        return headers

    # -----------------------------------------------------------------------

    @staticmethod
    def getsize_from_iterator(iterator):
        """Calculate the total size of data from an iterator.

        :param iterator: (iterable) The iterator to calculate the size of.

        :return: (tuple)
                - total_size (int): The total size in bytes.
                - new_iterator (generator): A new iterator with the same content.
        """
        chunks = list(iterator)  # Consume the iterator
        total_size = sum(len(chunk) for chunk in chunks)  # Calculate total size

        # Create a new iterator from the consumed data
        def recreate_iterator():
            for chunk in chunks:
                yield chunk

        return total_size, recreate_iterator()

    # -----------------------------------------------------------------------
    # PRIVATE METHODS
    # -----------------------------------------------------------------------

    def __get_headers_value(self, key: str, default_value: object = None) -> object:
        """Get headers value for a given key, try different keys format depending on server (httpd or wsgi).

        :param key: (str) the header key
        :param default_value: (object) optional parameter, value returned if the header doesn't contain the key
        :return: (object) the value in the header or the default value

        """
        value = self.__headers.get(key)

        # first key not found
        if value is None:
            # convert to wsgi key
            new_key = key.upper().replace('-', '_')
            value = self.__headers.get(new_key)

            # key not found again
            if value is None:
                new_key = "HTTP_" + new_key
                value = self.__headers.get(new_key)

                if value is None:
                    return default_value

        return value

    # -----------------------------------------------------------------------

    def __open_file_to_binary(self, filepath: str) -> bytes:
        """Open and read the given file and transform the content to bytes value.

        :param filepath: (str) The path of the file to read
        :return: (bytes|iterator) the file content in bytes format

        """
        if self.__get_headers_value("Content-Type") is None:
            file_type = HTTPDHandlerUtils.get_mime_type(filepath)
        else:
            file_type = self.__get_headers_value("Content-Type")

        if file_type is not None and (file_type.startswith("text/")
                                      or file_type == "application/javascript"
                                      or file_type == "application/json"):
            with codecs.open(filepath, "r", "utf-8") as fp:
                content = bytes("", "utf-8")
                for line in fp.readlines():
                    content += bytes(line, "utf-8")
                return content

        # Binary file
        sz = os.path.getsize(filepath)
        if sz < 100*1024*1024:  # 100Mo
            return open(filepath, "rb").read()

        # For large binary files, return an iterator to stream the content
        def file_iterator():
            with open(filepath, "rb") as fp:
                chunk = fp.read(8192)  # Read 8 KB chunks
                while chunk:
                    yield chunk
                    chunk = fp.read(8192)

        return file_iterator()

    # -----------------------------------------------------------------------

    def __extract_body_content(self, content) -> dict:
        """Read and parse the body content of a POST request.

        :param content: (Binary object) the body of the POST request
        :return: (dict) the dictionary that contains the events to process,
                        or an empty dictionary if there is an error.

        """
        # try to get the content type
        content_type = self.__get_headers_value("Content-Type")

        # try to get the content length
        content_length = self.__get_headers_value("Content-Length", "0")
        try:
            content_length = int(content_length)
        # if the length is None or not a string which contains an integer if somebody set the header with bad values
        except (TypeError, ValueError):
            content_length = 0

        # read request body and decode them
        data = content.read(content_length)

        try:
            data = data.decode("utf-8")
            # the data can't be decoded in utf-8 format: like an image or a video file.
            # it also happens if filename contains diacritics.
        except UnicodeError:
            logging.debug("Not an utf-8 content.")
            pass

        # if content-type or content_length are not defined in the header request
        if content_type is None or content_length == 0:
            data = dict()

        # parse json data from request.js
        elif "application/json" in content_type:
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                logging.error(f"Can't decode JSON posted data : {data}")

        # parse uploaded file
        elif "multipart/form-data; boundary=" in content_type:
            if isinstance(data, bytes) is True:
                filename, mime_type, content = HTTPDHandlerUtils.__extract_binary_form_data_file(content_type, data)
            else:
                filename, mime_type, content = HTTPDHandlerUtils.__extract_form_data_file(content_type, data)
            data = {'upload_file': {'filename': filename, 'mime_type': mime_type, 'file_content': content}}

        # otherwise try to parse text data from forms
        else:
            data = dict(parse_qsl(
                data,
                keep_blank_values=True,
                strict_parsing=False  # errors are silently ignored
            ))

        # print traceback and return data parsed in python dictionary
        if "upload_file" in data:
            logging.debug(f" -- upload_file[{data['upload_file']['filename']}]")

        return data

    # -----------------------------------------------------------------------

    @staticmethod
    def __extract_form_data_file(content_type: str, data: str) -> tuple[str, str, str]:
        """Extract the body of a "formdata request" to upload a file.

        Use this function with an utf-8 file content.

        :param content_type: (str) The content type in the header of the request
        :param data: (str | bytes) the body of the request in bytes or string format
        :return: (tuple[str, str, str]) the data extracted : filename, fime mime type and file content

        """
        # parse filename
        filename, end_index_filename = HTTPDHandlerUtils.__extract_form_data_filename(data)
        data = data[end_index_filename:]  # remove filename line

        # parse content-type
        mimetype, end_index_type = HTTPDHandlerUtils.__extract_form_data_mimetype(data)
        data = data[end_index_type + 1:]  # remove content-type line

        # parse file content
        boundary = HTTPDHandlerUtils.__extract_form_data_boundary(content_type)

        start_content = data.index("\n") + 1  # remove empty line
        end_content = data[start_content:].index(boundary)
        content = data[start_content:end_content]
        content = content.replace('\r', '')  # remove duplicate carriage return for new line

        return filename, mimetype, content

    # -----------------------------------------------------------------------

    @staticmethod
    def __extract_binary_form_data_file(content_type: str, data: bytes) -> tuple:
        """Extract the body of a "formdata request" to upload a file.

        Use this function with a binary file content.

        :param content_type: (str) The content type in the header of the request
        :param data: (str | bytes) the body of the request in bytes or string format
        :return: (tuple[str, str, str]) the data extracted : filename, fime mime type and file content

        """
        # extract prefix data
        file_content_begin = None
        content_type_pass = False
        prefix = ""

        for i in range(len(data)):
            # if we found a no ascii character (binary data of the file content)
            if data[i] <= 127:
                prefix += chr(data[i])
            else:
                file_content_begin = i
                break

            # if we pass the content-type data, and we finished the line then the next things is the file content
            if content_type_pass is True:
                index = prefix.index("Content-Type")
                if '\n\n' in prefix[index:] or '\r\n\r\n' in prefix[index:]:
                    file_content_begin = i + 1
                    break

            # check if we pass the content-type data (last data before the file content)
            if content_type_pass is False and "Content-Type" in prefix:
                content_type_pass = True

        # extract postfix data
        reversed_boundary = HTTPDHandlerUtils.__extract_form_data_boundary(content_type)[::-1]
        file_content_end = None
        postfix = ""

        for i in range(len(data) - 1, file_content_begin, -1):
            if reversed_boundary not in postfix:
                postfix += chr(data[i])
            else:
                file_content_end = i
                break

        # get variables to return
        content = data[file_content_begin:file_content_end + 1]
        filename = HTTPDHandlerUtils.__extract_form_data_filename(prefix)[0]
        mimetype = HTTPDHandlerUtils.__extract_form_data_mimetype(prefix)[0]

        return filename, mimetype, content

    # -----------------------------------------------------------------------

    @staticmethod
    def __extract_form_data_filename(text: str) -> tuple[str, int]:
        """Extract the filename from the form data uploaded file.

        :param text: (str) the body or a part received from the request.
        :return: (tuple[str, str, str]) the filename and the index where the filename value ends.

        """
        start_index_filename = text.index('filename="') + len('filename="')
        end_index_filename = start_index_filename + text[start_index_filename:].index('"')

        return text[start_index_filename:end_index_filename], end_index_filename

    # -----------------------------------------------------------------------

    @staticmethod
    def __extract_form_data_mimetype(text: str) -> tuple[str, int]:
        """Extract the mimetype from the form data uploaded file.

        :param text: (str) the body or a part received from the request.
        :return: (tuple[str, str, str]) the mimetype and the index where the mimetype value ends.

        """
        start_index_type = text.index("Content-Type: ") + len("Content-Type: ")
        end_index_type = start_index_type + text[start_index_type:].index("\n")
        mimetype = text[start_index_type:end_index_type]
        mimetype = mimetype.replace("\r", '')

        return mimetype, end_index_type

    # -----------------------------------------------------------------------

    @staticmethod
    def __extract_form_data_boundary(content_type: str) -> str:
        """Extract the boundary from the form data content type which delimited the uploaded file content.

        :param content_type: (str) the content type in the header of the received request.
        :return: (tuple[str, str, str]) the boundary.

        """
        start_boundary = content_type.index("boundary=") + len("boundary=")
        boundary = "--" + content_type[start_boundary:] + "--"

        return boundary
