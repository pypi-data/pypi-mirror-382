# -*- coding: UTF-8 -*-
"""
:filename: whakerpy.htmlmaker.treeerror.py
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: Root of the tree to store HTML elements and serialize into a string.

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

from .treenode import HTMLTree


class HTMLTreeError(HTMLTree):

    def __init__(self, status, msg_error: str = None):
        """Create an HTML Tree for status error response.

        :param status: (HTTPDStatus) The status of the response. (DO NOT typing it for circular import problem)
        :param msg_error: (str) Optional parameter, error message to display in the page for more information

        """
        text = f"{status.code} : {status.HTTPD_STATUS[status.code]}"

        super(HTMLTreeError, self).__init__(f"tree_{status.code}")
        self.head.title(text)

        h1 = self.element("h1")
        h1.set_value(text)

        if msg_error is not None:
            html_error = self.element("p")
            html_error.set_value(msg_error)
