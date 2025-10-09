"""
:filename: whakerpy.webapp.webresponse.py
:author: Brigitte Bigi
:contributor: Mathias Cazals
:contact: contact@sppas.org
:summary: Create a generic HTTPD response for a web server.

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

import logging
import codecs

from whakerpy.httpd import HTTPDStatus
from whakerpy.httpd import BaseResponseRecipe

# ---------------------------------------------------------------------------


class WebSiteResponse(BaseResponseRecipe):
    """Create an HTML response content.

    Can be used when all pages of a webapp are sharing the same header, nav
    and footer. Then, **only one tree** is created for all pages, and its
    body->main is changed depending on the requested page.

    """

    def __init__(self, name="index.html", tree=None, **kwargs):
        """Create a HTTPD Response instance with a default response.

        Useful when creating dynamically the HTML Tree for a webapp.
        The "main" part of the body is re-created every time bake() is invoked.
        Here, it's loaded from a static file.

        :param name: (str) Filename of the body main content.

        """
        self._name = name

        # Inheritance with a given dynamic HTMLTree.
        super(WebSiteResponse, self).__init__(name, tree)

        # Create the dynamic HTTPD response content
        self._status = HTTPDStatus()
        self._bake()

    # -----------------------------------------------------------------------

    def page(self) -> str:
        """Override. Return the current HTML page name.

        :return: (str) Name of the file containing the body->main.

        """
        return self._name

    # -----------------------------------------------------------------------

    def _process_events(self, events, **kwargs) -> bool:
        """Process the given events.

        The given event name must match a function of the event's manager.
        Processing an event may change the content of the tree. In that case,
        the `dirty` method must be turned into True: it will invalidate the
        deprecated content (_invalidate) and re-generate a new one (_bake).

        :param events (dict): key=event_name, value=event_value
        :return: (bool)

        """
        self._status.code = 200
        return True   # Always invalidate/bake the body->main.

    # -----------------------------------------------------------------------

    def _invalidate(self) -> None:
        """Remove all children nodes of the body "main".

        Delete the body main content and nothing else.

        """
        node = self._htree.body_main
        node.clear_children()

    # -----------------------------------------------------------------------

    def _bake(self) -> None:
        """Create the dynamic page content in HTML.

        Load the body->main content from a file and add it to the tree.

        """
        logging.debug(" -> Set {:s} content to the body->main".format(self._name))
        # Define this page main content.
        with codecs.open(self._name, "r", "utf-8") as fp:
            lines = fp.readlines()
            if self._htree.get_body_main() is not None:
                self._htree.body_main.set_value(" ".join(lines))
