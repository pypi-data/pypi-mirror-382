"""
:filename: whakerpy.htmlmaker.emptynodes.emptyelts.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: A set of specific nodes of the tree.

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

from ..hconsts import HTML_GLOBAL_ATTR
from ..hexc import NodeAttributeError

from .emptynode import EmptyNode

# ---------------------------------------------------------------------------


class HTMLInputText(EmptyNode):
    """Represent an input text element of a form.

    The set_attribute method should be overridden to check if the given key
    is in the list of accepted attributes.

    """

    def __init__(self, parent, identifier):
        """Create an input node. Default type is 'text'. """
        super(HTMLInputText, self).__init__(parent, identifier, "input")
        self.set_attribute("type", "text")
        self.set_attribute("id", identifier)
        self.set_attribute("name", identifier)

    # -----------------------------------------------------------------------

    def set_name(self, name):
        """Set input name attribute, and 'id' too.

        :param name: (str)

        """
        self.set_attribute("id", name)
        self.set_attribute("name", name)

# ---------------------------------------------------------------------------


class HTMLImage(EmptyNode):
    """Represent an image element.

    The set_attribute method should be overridden to check if the given key
    is in the list of accepted attributes.

    """
    def __init__(self, parent: str, identifier: str, src: str):
        """Create an image leaf node.

        :param parent: (str) Identifier of the parent node
        :param identifier: (str | None) Identifier to assign to the image
        :param src: (str) Image source relative path

        """
        super(HTMLImage, self).__init__(parent, identifier, "img")
        self.add_attribute("src", src)
        self.add_attribute("alt", "")

# ---------------------------------------------------------------------------


class HTMLHr(EmptyNode):
    """Represent a horizontal line with &lt;hr&gt; tag.

    The &lt;hr&gt; tag only supports the Global Attributes in HTML.

    """

    def __init__(self, parent: str):
        """Create a node for &lt;hr&gt; tag.

        """
        super(HTMLHr, self).__init__(parent, None, "hr")

    # -----------------------------------------------------------------------

    def check_attribute(self, key: str) -> str:
        """Override.

        :return: key (str)
        :raises: NodeAttributeError: if given key can't be converted to string
        :raises: NodeAttributeError: The attribute can't be assigned to this element.

        """
        try:
            key = str(key)
        except Exception:
            raise NodeAttributeError(key)

        if key not in HTML_GLOBAL_ATTR and key.startswith("data-") is False:
            raise NodeAttributeError(key)

        return key

# ---------------------------------------------------------------------------


class HTMLBr(EmptyNode):
    """Represent a new line with &lt;br&gt; tag.

    The &lt;br&gt; tag does not support any attribute.

    """

    def __init__(self, parent: str):
        """Create a node for &lt;br&gt; tag.

        """
        super(HTMLBr, self).__init__(parent, None, "br")

    # -----------------------------------------------------------------------

    def check_attribute(self, key: str) -> str:
        """Override. Raise an exception because no attribute is supported.

        :raises: NodeAttributeError: The attribute can't be assigned to this element.

        """
        raise NodeAttributeError(key)

