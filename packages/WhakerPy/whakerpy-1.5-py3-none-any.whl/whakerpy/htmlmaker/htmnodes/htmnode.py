"""
:filename: whakerpy.htmlmaker.htmnodes.htmnode.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Node classes to generate HTML elements.

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
import traceback

from ..hconsts import HTML_TAGS
from ..hexc import NodeParentIdentifierError
from ..hexc import NodeTypeError
from ..hexc import NodeKeyError
from ..hexc import NodeTagError
from ..emptynodes import BaseTagNode

# ---------------------------------------------------------------------------


class TagNode(BaseTagNode):
    """A node for any HTML element.

    This node can't check the integrity of the tree: it knows only both its
    direct parent and children but not all its predecessors nor all its
    successors. And no recursive search is implemented.

    This class can deal with elements like for example:

        - &lt;tag/&gt;
        - &lt;tag k=v /&gt;
        - &lt;tag k1=v1 k2=v2 k3/&gt;
        - &lt;tag&gt; value [children]* &lt;/tag&gt;
        - &lt;tag k=v&gt; value &lt;/tag&gt;
        - &lt;tag k1=v1 k2=v2 k3&gt; value &lt;/tag&gt;
        - ...

    This class can't have children inside its value like for example:

        - &lt;tag&gt; value_part1 &lt;b&gt; text_bold &lt;/b&gt; value_part2 &lt;/tag&gt;

    To work around this limitation, let value be the whole content of the
    tag. In the example, value is "value_part1 <b> text_bold </b> value_part2"
    and the tag has no <b> child.

    """

    def __init__(self, parent: str | None, identifier: str, tag: str, attributes=dict(), value=None):
        """Create a tag node to represent any HTML element.

        :param parent: (str) Parent identifier
        :param identifier: (str) This node identifier

        """
        # Identifier(s) of the children' node(s) :
        self._children = list()

        super(TagNode, self).__init__(parent, identifier, tag, attributes)

        # The node data
        self._value = value

    # -----------------------------------------------------------------------
    # Tree management: getters and setters
    # -----------------------------------------------------------------------

    def get_nidx_child(self, child_idx: int):
        """Return a direct child of the node or None.

        :param child_idx: (int) Child index
        :return: (HTMLNode)
        :raises: IndexError

        """
        child_idx = int(child_idx)
        if 0 <= child_idx < len(self._children):
            return self._children[child_idx]
        raise IndexError("Invalid index {:d} to get access to a child."
                         "".format(child_idx))

    # -----------------------------------------------------------------------

    def get_child(self, child_id: str):
        """Return a direct child of the node or None.

        :param child_id: (str) Child identifier
        :return: (HTMLNode | None)

        """
        for child in self._children:
            if child.identifier == child_id:
                return child
        return None

    # -----------------------------------------------------------------------

    def children_size(self) -> int:
        """Return the number of direct children.

        :return: (int)

        """
        return len(self._children)

    # -----------------------------------------------------------------------

    def has_child(self, node_id: str) -> bool:
        """Return True if the given node is a direct child.

        :param node_id: (str) Identifier of the node
        :return: (bool) True if given identifier is a direct child.

        """
        return node_id in [child.identifier for child in self._children]

    # -----------------------------------------------------------------------

    def append_child(self, node) -> None:
        """Append a child node.

        :param node: (BaseNode, BaseTagNode, EmptyNode, HTMLNode)
        :raises: TypeError:
        :raises: NodeKeyError:
        :raises: NodeParentIdentifierError:

        """
        # if isinstance(node, BaseNode) is False:
        #     raise TypeError("Node expected.")
        if hasattr(node, 'identifier') is False:
            raise NodeTypeError(type(node))

        if node.identifier == self._parent or node.identifier == self.identifier:
            raise NodeKeyError(self.identifier, node.identifier)

        if node.get_parent() != self.identifier:
            raise NodeParentIdentifierError(self.identifier, node.get_parent())

        if node not in self._children:
            self._children.append(node)

    # -----------------------------------------------------------------------

    def insert_child(self, pos: int, node):
        """Insert a child node at the given index.

        :param pos: (int) Index position
        :param node: (BaseNode, BaseTagNode, EmptyNode, HTMLNode)
        :raises: NodeKeyError:
        :raises: TypeError:
        :raises: Exception:

        """
        # if isinstance(node, BaseNode) is False:
        #    raise TypeError("Node expected.")
        if hasattr(node, 'identifier') is False:
            raise NodeTypeError(type(node))

        if node.identifier == self._parent or node.identifier == self.identifier:
            raise NodeKeyError(self.identifier, node.identifier)

        if node.get_parent() != self.identifier:
            raise NodeParentIdentifierError(self.identifier, node.get_parent())

        if node not in self._children:
            self._children.insert(pos, node)

    # -----------------------------------------------------------------------

    def remove_child(self, node_id: str) -> None:
        """Remove a child node.

        :param node_id: (str)

        """
        node = None
        for n in self._children:
            if n.identifier == node_id:
                node = n
                break
        if node is not None:
            self._children.remove(node)

    # -----------------------------------------------------------------------

    def pop_child(self, pos: int) -> None:
        """Remove a child node from its index.

        :param pos: (int) Index position of the child
        :raises: IndexError: incorrect given position

        """
        self._children.pop(pos)

    # -----------------------------------------------------------------------

    def clear_children(self) -> None:
        """Remove all children of the node."""
        self._children.clear()

    # -----------------------------------------------------------------------
    # HTML management: getters and setters
    # -----------------------------------------------------------------------

    def is_leaf(self) -> bool:
        """Return true if node has no children."""
        return len(self._children) == 0

    # -----------------------------------------------------------------------

    def get_value(self) -> str:
        """Return the tag content value."""
        return self._value

    # -----------------------------------------------------------------------

    def set_value(self, value: str):
        """Set or re-set the tag content value."""
        self._value = str(value)

    # -----------------------------------------------------------------------
    # HTML management: HTML generator
    # -----------------------------------------------------------------------

    def serialize(self, nbs: int = 4) -> str:
        """Serialize the node into HTML.

        :param nbs: (int) Number of spaces for the indentation
        :return: (str)

        """
        indent = " "*nbs
        # Element begin tag
        html = indent + "<" + self.tag
        for key in self._attributes:
            html += " "
            html += key
            if self._attributes[key] is not None:
                html += '="'
                html += self._attributes[key]
                html += '"'
        html += ">"
        # Element value or children nodes
        if self._value is not None or len(self._children) > 0:
            html += "\n"
            if self._value is not None:
                html += self.__serialize_value(indent, nbs)
            for node_id in self._children:
                html += node_id.serialize(nbs+4)
            html += indent
        # Element end tag
        html += "</" + self.tag + ">\n"
        return html

    # -----------------------------------------------------------------------

    def __serialize_value(self, indent, nbs):
        html = ""
        try:
            # For some tags, the space char is meaningful. textarea is one of them. others???
            if self.tag != "textarea":
                html += indent + " " * nbs
            html += self._value
            html += "\n"
        except TypeError as e:
            logging.error(str(e))
            if logging.getLogger().getEffectiveLevel() == 0:
                traceback.print_exc()
            html += indent + "    'Unexpected data type'"
            html += "\n"
        return html

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __str__(self):
        name = self.__class__.__name__
        kwargs = [
            "tag={0}".format(self.tag),
            "identifier={0}".format(self.identifier),
            "attributes={0}".format(self._attributes),
        ]
        return "%s(%s)" % (name, ", ".join(kwargs))

# ---------------------------------------------------------------------------


class HTMLNode(TagNode):

    def __init__(self, parent: str, identifier: str, tag: str, attributes=dict(), value=None):
        """Create a tag node to represent any HTML element.

        :param parent: (str) Parent identifier
        :param identifier: (str) This node identifier
        :raises: NodeTagError: Invalid tag. Not in the HTML_TAGS list.

        """
        # Identifier(s) of the children' node(s) :
        self._children = list()

        super(HTMLNode, self).__init__(parent, identifier, tag, attributes)
        if self.tag not in HTML_TAGS.keys():
            raise NodeTagError(tag)

        # The node data
        self._value = value
