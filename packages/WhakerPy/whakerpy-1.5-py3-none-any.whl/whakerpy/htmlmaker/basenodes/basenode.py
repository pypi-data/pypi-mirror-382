"""
:filename: whakerpy.htmlmaker.basenodes.basenode.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: A base class for any HTML element.

.. _This file was initially part of SPPAS: https://sppas.org/
.. _This file is now part of WhakerPy: https://whakerpy.sourceforge.io
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

import re
import uuid

from whakerpy.htmlmaker.hexc import NodeInvalidIdentifierError
from whakerpy.htmlmaker.hexc import NodeKeyError

# ---------------------------------------------------------------------------


class BaseNode(object):
    """A base class for any node in an HTML tree.

    An HTML element without content is called an empty node. It has a
    start tag but neither a content nor an end tag. It has only attributes.

    The BaseNode() class is a base class for any of these HTML elements.
    It is intended to be overridden.

    """

    def __init__(self, parent: str = None, identifier: str = None, **kwargs):
        """Create a new base node.

        :param parent: (str) Parent identifier
        :param identifier: (str) This node identifier
        :raises: NodeInvalidIdentifierError: if 'identifier' contains invalid characters or if invalid length

        """
        # The node identifier
        if identifier is not None:
            ident = BaseNode.validate_identifier(identifier)
            self.__identifier = ident
        else:
            self.__identifier = str(uuid.uuid1())

        # Identifier of the parent node
        self._parent = None
        self.set_parent(parent)

    # -----------------------------------------------------------------------

    @staticmethod
    def validate_identifier(identifier: str) -> str:
        """Return the given identifier if it matches the requirements.

        An identifier should contain at least 1 character and no whitespace.

        :param identifier: (str) Key to be validated
        :raises: NodeInvalidIdentifierError: if it contains invalid characters
        :raises: NodeInvalidIdentifierError: if invalid length
        :return: (str) Validated identifier

        """
        entry = BaseNode.full_strip(identifier)
        if len(entry) != len(identifier):
            raise NodeInvalidIdentifierError(identifier)

        if len(identifier) == 0:
            raise NodeInvalidIdentifierError(identifier)

        return identifier

    # -----------------------------------------------------------------------

    @staticmethod
    def full_strip(entry):
        """Fully strip the string: multiple whitespace, tab and CR/LF.

        :return: (str) Cleaned string

        """
        e = re.sub("[\\s]+", r"", entry)
        e = re.sub("[\\t]+", r"", e)
        e = re.sub("[\\n]+", r"", e)
        e = re.sub("[\\r]+", r"", e)
        if "\ufeff" in e:
            e = re.sub("\ufeff", r"", e)
        return e

    # -----------------------------------------------------------------------

    @property
    def identifier(self) -> str:
        """Return the (supposed-) unique ID of the node within the scope of a tree. """
        return self.__identifier

    # -----------------------------------------------------------------------

    def is_leaf(self) -> bool:
        """Return true if node has no children."""
        return True

    # -----------------------------------------------------------------------

    def is_root(self) -> bool:
        """Return true if node has no parent, i.e. like root."""
        return self._parent is None

    # -----------------------------------------------------------------------

    def get_parent(self) -> str:
        """The parent identifier.

        :return: (str) node identifier

        """
        return self._parent

    # -----------------------------------------------------------------------

    def set_parent(self, node_id: str) -> None:
        """Set the parent identifier.

        :param node_id: (str) Identifier of the parent

        """
        if self.__identifier == node_id:
            raise NodeKeyError(self.__identifier, node_id)

        self._parent = node_id

    # -----------------------------------------------------------------------

    def has_child(self, node_id: str) -> bool:
        """To be overriden. Return True if the given node ID is a direct child.

        :param node_id: (str) Identifier of the node
        :return: (bool) True if given identifier is a direct child.

        """
        return not self.is_leaf()

    # -----------------------------------------------------------------------

    def serialize(self, nbs: int = 4) -> str:
        """To be overriden. Serialize the node into HTML.

        :param nbs: (int) Number of spaces for the indentation
        :return: (str)

        """
        return ""

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __repr__(self):
        return self.serialize()

    # -----------------------------------------------------------------------

    def __str__(self):
        return "Node ({:s})".format(self.identifier)
