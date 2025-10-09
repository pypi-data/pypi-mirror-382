"""
:filename: whakerpy.htmlmaker.emptynodes.emptynode.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: A node with an HTML empty element.

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
from ..hexc import NodeAttributeError
from ..hexc import NodeTagError
from ..basenodes import BaseNode
from ..hconsts import HTML_EMPTY_TAGS
from ..hconsts import HTML_TAG_ATTR
from ..hconsts import HTML_GLOBAL_ATTR
from ..hconsts import HTML_VISIBLE_ATTR
from ..hconsts import ARIA_TAG_ATTR

# ---------------------------------------------------------------------------


class BaseTagNode(BaseNode):
    """A node to represents an HTML element with attributes.

    An HTML element without content is called an empty node. It has a
    start tag but neither a content nor an end tag.
    Compared to the parent class BaseNode, this class adds 2 members:

    1. the required element tag;
    2. its optional attributes.

    For example, it can deal with elements like:

    - &lt;tag /&gt;
    - &lt;tag k=v /&gt;
    - &lt;tag k1=v2 k2=v2 k3 /&gt;

    """

    def __init__(self, parent: str | None, identifier: str, tag: str, attributes: dict = dict()):
        """Create a new empty node.

        :param parent: (str) Parent identifier
        :param identifier: (str) This node identifier
        :param tag: (str) The element tag. Converted in lower case.
        :param attributes: (dict) key=(str) value=(str or None)
        :raises: NodeInvalidIdentifierError:
        :raises: NodeTagError:
        :raises: TypeError:

        """
        super(BaseTagNode, self).__init__(parent, identifier)

        # The node data: a tag and its attributes
        tag = str(tag)
        self.__tag = tag.lower()
        self._attributes = dict()

        # Fill in the attributes' dictionary
        if isinstance(attributes, dict) is False:
            raise TypeError("Expected a dict for the attributes argument of BaseTagNode().")
        for key in attributes:
            value = attributes[key]
            self.add_attribute(key, value)

    # -----------------------------------------------------------------------
    # HTML management: getters and setters
    # -----------------------------------------------------------------------

    @property
    def tag(self) -> str:
        """Return the HTML tag. """
        return self.__tag

    # -----------------------------------------------------------------------

    def check_attribute(self, key) -> str:
        """Raises NodeAttributeError if key is not a valid attribute.

        :param key: (any) An attribute
        :raises: NodeAttributeError: The attribute can't be assigned to this element.
        :raises: NodeAttributeError: if given key can't be converted to string
        :return: key (str) valid key

        """
        try:
            key = str(key)
            key = key.lower()
        except Exception:
            raise NodeAttributeError(key)

        if key not in HTML_GLOBAL_ATTR and \
                key.startswith("data-") is False and \
                key not in HTML_VISIBLE_ATTR and \
                key not in HTML_TAG_ATTR.keys() and \
                key not in ARIA_TAG_ATTR.keys():
            raise NodeAttributeError(key)

        return key

    # -----------------------------------------------------------------------

    def get_attribute_keys(self) -> list:
        """Return the list of attribute keys. """
        return [k for k in self._attributes.keys()]

    # -----------------------------------------------------------------------

    def set_attribute(self, key: str, value) -> str:
        """Set a property to the node. Delete the existing one, if any.

        :param key: Key property
        :param value: (str or list)
        :raises: NodeAttributeError: The attribute can't be assigned to this element.
        :raises: NodeAttributeError: if given key can't be converted to string
        :return: key (str) valid assigned key

        """
        key = self.check_attribute(key)
        if isinstance(value, (list, tuple)) is True:
            value = " ".join(value)
        self._attributes[key] = value
        return key

    # -----------------------------------------------------------------------

    def add_attribute(self, key: str, value) -> str:
        """Add a property to the node. Append the value if existing.

        :param key: (str) Key property
        :param value:
        :raises: NodeAttributeError: The attribute can't be assigned to this element.
        :raises: NodeAttributeError: if given key can't be converted to string
        :return: key (str) valid assigned key

        """
        if key not in self._attributes:
            self.set_attribute(key, value)
        else:
            if self._attributes[key] is not None:
                self._attributes[key] += " " + value
            else:
                self._attributes[key] = value
        return key

    # -----------------------------------------------------------------------

    def get_attribute_value(self, key: str):
        """Return the attribute value if the node has this attribute.

        :param key: (str) Attribute key
        :return: (str | None) Value or None if the attribute does not exist or has no value

        """
        if key in self._attributes:
            return self._attributes[key]
        return None

    # -----------------------------------------------------------------------

    def has_attribute(self, key: str) -> bool:
        """Return true if the node has the attribute.

        :param key: (str) Attribute key
        :return: (bool)

        """
        return key in self._attributes

    # -----------------------------------------------------------------------

    def remove_attribute(self, key: str) -> None:
        """Remove the attribute to the node.

        :param key: (str) Attribute key

        """
        if key in self._attributes:
            del self._attributes[key]

    # -----------------------------------------------------------------------

    def remove_attribute_value(self, key: str, value: str) -> None:
        """Remove the value of an attribute of the node.

        :param key: (str) Attribute key
        :param value: (str) Attribute value

        """
        if key in self._attributes:
            values = self._attributes[key].split(" ")
            if value in values:
                values.remove(value)
                if len(values) == 0:
                    del self._attributes[key]
                else:
                    self.set_attribute(key, " ".join(values))

    # -----------------------------------------------------------------------

    def nb_attributes(self) -> int:
        """Return the number of attributes. """
        return len(self._attributes)

    # -----------------------------------------------------------------------
    # HTML management: HTML generator
    # -----------------------------------------------------------------------

    def serialize(self, nbs: int = 4) -> str:
        """Override. Serialize the node into HTML.

        :param nbs: (int) Number of spaces for the indentation
        :return: (str)

        """
        indent = " "*nbs
        html = indent + "<" + self.__tag
        for key in self._attributes:
            html += " "
            html += key
            value = self._attributes[key]
            if value is not None:
                html += '="'
                html += value
                html += '"'
        html += " />\n"

        return html

# ---------------------------------------------------------------------------


class EmptyNode(BaseTagNode):
    """A node to represents an HTML empty element.

    An HTML element without content is called an empty node. It has a
    start tag but neither a content nor an end tag.

    """

    def __init__(self, parent: str, identifier: str, tag: str, attributes: dict = dict()):
        """Create a new empty node.

        :param parent: (str) Parent identifier
        :param identifier: (str) This node identifier
        :param tag: (str) The element tag
        :param attributes: (dict) key=(str) value=(str or None)
        :raises: NodeInvalidIdentifierError:
        :raises: NodeTagError:
        :raises: TypeError:

        """
        super(EmptyNode, self).__init__(parent, identifier, tag, attributes)
        if self.tag not in HTML_EMPTY_TAGS.keys():
            raise NodeTagError(tag)
