"""
:filename: whakerpy.httpd.hresponse.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Base class to create an HTML response.

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
import os
import json

from whakerpy.htmlmaker import HTMLComment
from whakerpy.htmlmaker import HTMLNode
from whakerpy.htmlmaker import HTMLTree

from .hstatus import HTTPDStatus

# ---------------------------------------------------------------------------


class BaseResponseRecipe:
    """Base class to create an HTML response content.

    """

    @staticmethod
    def page() -> str:
        """Return the HTML page name. To be overridden."""
        return "undefined.html"

    # -----------------------------------------------------------------------

    def __init__(self, name="Undefined", tree=None):
        """Create a new ResponseRecipe instance with a default response.

        """
        # Define members with default values
        self._name = name
        self._status = HTTPDStatus()
        # Data to communicate with client (javascript side)
        self._data = dict()

        # Define workers: the HTML bakery
        if tree is not None and isinstance(tree, HTMLTree):
            self._htree = tree
        else:
            self._htree = HTMLTree(self._name.replace(" ", "_"))

        # Fill-in the tree with nodes
        self.create()

    # -----------------------------------------------------------------------

    def get_data(self) -> str | bytes:
        """Gets the current data to send to the client following this request.

        :return: (str) The data in the string format or json depending on the type.

        """
        if isinstance(self._data, dict):
            return json.dumps(self._data)

        elif isinstance(self._data, bytes) or isinstance(self._data, bytearray) or isinstance(self._data, str):
            return self._data

        else:
            raise ValueError(f"Unexpected data type to response to the client : {type(self._data)}")

    # -----------------------------------------------------------------------

    def reset_data(self) -> None:
        """Clear json data of the response.
        This function has to be called after each response send to the client to avoid overflow problems.

        """
        self._data = dict()

    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------

    @property
    def name(self) -> str:
        return self._name

    @property
    def status(self) -> HTTPDStatus:
        return self._status

    # -----------------------------------------------------------------------
    # Convenient methods to add HTML nodes in the body part of the tree
    # -----------------------------------------------------------------------

    def comment(self, content: str) -> HTMLComment:
        """Add a comment to the body->main.

        :param content: (str) The comment content
        :return: (HTMLComment) the created node

        """
        return self._htree.comment(content)

    # -----------------------------------------------------------------------

    def element(self, tag: str = "div", ident=None, class_name=None) -> HTMLNode:
        """Add an element node to the body->main.

        :param tag: (str) HTML element name
        :param ident: (str) Identifier of the element
        :param class_name: (str) Value of the class attribute
        :return: (HTMLNode) The created node

        """
        return self._htree.element(tag, ident, class_name)

    # -----------------------------------------------------------------------
    # Workers
    # -----------------------------------------------------------------------

    def create(self) -> None:
        """Create the fixed page content in HTML. Intended to be overridden.

        This method is intended to be used to create the parts of the tree
        that won't be invalidated when baking.

        """
        pass

    # -----------------------------------------------------------------------

    def bake(self, events: dict, headers: dict = None) -> str:
        """Return the HTML response after processing the events.

        Processing the events may change the response status. This method is
        invoked by the HTTPD server to construct the response. Given events
        are the information the handler received (commonly with POST).

        :param events: (dict) The requested events to be processed
        :param headers: (dict) The headers of the http request received

        """
        # Process the given events with the application
        dirty = self._process_events(events, headers=headers)

        # Re-create the page content only if something changed during
        # processing the events.
        if dirty is True:
            self._invalidate()
            self._bake()

        # Turn the page content into an HTML string.
        return self._htree.serialize()

    # -----------------------------------------------------------------------
    # Private: methods to be overridden by children to customize the recipe.
    # -----------------------------------------------------------------------

    def _process_events(self, events: dict, **kwargs) -> bool:
        """Process the given events.

        The given event name must match a function of the event's manager.
        Processing an event may change the content of the tree. In that case,
        the `dirty` method must be turned into True: it will invalidate the
        deprecated content (_invalidate) and re-generate a new one (_bake).

        :param events (dict): key=event_name, value=event_value
        :return: (bool)

        """
        self._status.code = 200
        return False

    # -----------------------------------------------------------------------

    def _invalidate(self):
        """Remove children nodes of the tree. Intended to be overridden.

        Remove the dynamic content of the tree, which will be re-introduced
        when baking.

        If the tree has no dynamic content, this method is un-used.

        """
        pass

    # -----------------------------------------------------------------------

    def _bake(self) -> None:
        """Fill in the HTML page generator. Intended to be overridden.

        If the tree has no dynamic content, this method is un-used.

        This method is baking the "dynamic" content of the page, i.e. it
        should not change the content created by the method create().

        """
        pass
