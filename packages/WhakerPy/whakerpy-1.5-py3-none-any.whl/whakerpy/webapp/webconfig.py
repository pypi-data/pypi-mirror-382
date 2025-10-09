"""
:filename: whakerpy.webapp.webconfig.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Store config data of a webapp from a JSON file.

.. _This file is part of WhakerPy: https://whakerpy.sourceforge.io
..
    -------------------------------------------------------------------------

    Copyright (C) 2023-2025 Brigitte Bigi
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
import codecs
import logging
import os
import json

from ..htmlmaker import HTMLTree
from ..httpd import BaseResponseRecipe

from .webresponse import WebSiteResponse

# ---------------------------------------------------------------------------


class WebSiteData:
    """Storage class for a web application configuration extracted from a JSON file.

    This class supports the creation of semi-dynamic HTML pages. Each page entry in the JSON
    is rendered using the same ResponseReceipe instance, with only the 'body->main' content
    loaded from a static file.

    For each semi-dynamic page, this class stores:
      - the page name (used in the URL),
      - the page title,
      - the local filename of the main body content.

    Example entry in the JSON file:
        "index.html": {
            "title": "Home",
            "main": "index.htm",
            "header": true,
            "footer": true
        }

    The 'bake_response' method can return a ResponseReceipe for any page—either semi-dynamic
    or fully dynamic. Note that '__contains__' only checks semi-dynamic pages, while 'is_page'
    identifies any page that can be baked.

    """

    def __init__(self, json_filename: str | None = None):
        """Create a WebSiteData instance.

        :param json_filename: (str) Configuration filename.

        """
        # Path to page files
        self._main_path = ""
        # Filename of the default page
        self._default = ""

        # Information of each page: filename, title, body main filename
        self._pages = dict()

        if json_filename is not None:
            section = self.__get_json_whakerpy_section(json_filename)
            for raw_name, info in section.items():
                # Web-page names are always lowered
                name = raw_name.lower()
                if name == "pagespath":
                    self._main_path = info
                else:
                    # Store mapping: URL page → info dict
                    self._pages[name] = info
                    # First non-default page
                    if self._default == "":
                        self._default = name
        else:
            logging.debug("WebSiteData with NO given JSON config filename.")

    # -----------------------------------------------------------------------

    @staticmethod
    def description() -> str:
        """To be overridden. Return a short description of the website."""
        return "No description provided."

    # ---------------------------------------------------------------------------

    @staticmethod
    def icon() -> str:
        """To be overridden. Return the path of the favicon of the website."""
        return ""

    # -----------------------------------------------------------------------

    @staticmethod
    def name() -> str:
        """To be overridden. Return a short name of the application."""
        return "NoName"

    # -----------------------------------------------------------------------

    def get_default_page(self) -> str:
        """Return the name of the default page."""
        return self._default

    # -----------------------------------------------------------------------

    def is_page(self, page_name: str) -> bool:
        """To be overridden. Return true if the given page name can be baked.

        :param page_name: The name of the page to check.
        :return: (bool) True if the given page name can be baked.

        """
        if page_name in self._pages:
            return True
        return False

    # -----------------------------------------------------------------------

    def filename(self, page: str) -> str:
        """Return the filename of a given page.

        :param page: (str) Name of an HTML page
        :return: (str)

        """
        if page in self._pages:
            main_name = self._pages[page]["main"]
            return os.path.join(self._main_path, main_name)

        return ""

    # -----------------------------------------------------------------------

    def title(self, page: str) -> str:
        """Return the title of a given page.

        :param page: (str) Name of an HTML page
        :return: (str)

        """
        if page in self._pages:
            if "title" in self._pages[page]:
                return self._pages[page]["title"]

        return ""

    # -----------------------------------------------------------------------

    def has_header(self, page: str) -> bool:
        """Return True if the given page should have the header.

        :param page: (str) Name of an HTML page
        :return: (bool)

        """
        if page in self._pages:
            if "header" in self._pages[page].keys():
                return self._pages[page]["header"]

        return False

    # -----------------------------------------------------------------------

    def has_footer(self, page: str) -> bool:
        """Return True if the given page should have the footer.

        :param page: (str) Name of an HTML page
        :return: (bool)

        """
        if page in self._pages:
            if "footer" in self._pages[page]:
                return self._pages[page]["footer"]

        return False

    # -----------------------------------------------------------------------

    def create_pages(self, web_response=WebSiteResponse, default_path: str = "") -> dict:
        """Instantiate all pages response from the json.

        :param web_response: (BaseResponseRecipe) the class to used to create the pages,
                            WebSiteResponse class used by default
        :param default_path: (str) None by default, the default path for all pages

        :return: (dict) a dictionary with key = page name and value = the response object

        """
        pages = dict()

        tree = HTMLTree("sample")
        for page_name in self._pages:
            page_path = os.path.join(default_path, self.filename(page_name))
            pages[page_name] = web_response(page_path, tree)

        return pages

    # -----------------------------------------------------------------------

    def bake_response(self, page_name: str, default: str = "") -> BaseResponseRecipe | None:
        """Return the bakery system to create the page dynamically.

        To be overridden by subclasses.

        :param page_name: (str) Name of an HTML page
        :param default: (str) The default path
        :return: (BaseResponseRecipe)

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __get_json_whakerpy_section(self, filename):
        """Return the configuration section related to WhakerPy.

        - Look for a top‐level "WhakerPy" key (new format).
        - Otherwise use the full JSON (old format) and issue a deprecation warning.

        :param filename: path to JSON configuration file
        :return: dict with keys "pagespath", "<page>.html", …
        :raises: FileNotFoundError: if the file cannot be opened
        :raises: OSError: on other I/O errors reading the file
        :raises: json.JSONDecodeError: if the file is not valid JSON
        :raises: ValueError: if the required "pagespath" key is missing

        """
        # may raise FileNotFoundError / OSError here
        with codecs.open(filename, "r", "utf-8") as f:
            _full_data = json.load(f)  # may raise JSONDecodeError

        if "WhakerPy" in _full_data:
            _section = _full_data["WhakerPy"]
        else:
            logging.warning(
                "DeprecationWarning: starting with WhakerPy 1.2 you must wrap your "
                "config in a top-level 'WhakerPy' key of the JSON config file."
            )
            _section = _full_data

        if "pagespath" not in _section:
            raise ValueError(
                f"{filename!r} missing required 'pagespath' in WhakerPy section"
            )

        return _section

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    def __iter__(self):
        for a in self._pages:
            yield a

    def __len__(self):
        return len(self._pages)

    def __contains__(self, value):
        """Value is a page name."""
        return value in self._pages
