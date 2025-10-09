"""
:filename: whakerpy.htmlmaker.treeelts.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Node classes to generate HTML elements.

.. _This file was initially part of SPPAS: https://sppas.org/
.. _This file is now part of WhakerPy: https://whakerpy.sourceforge.io
..
    -------------------------------------------------------------------------

    Copyright (C) 2023-2025 Brigitte Bigi, CNRS
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

import os

from .hexc import NodeChildTagError
from .hconsts import HEAD_TAGS
from .emptynodes import EmptyNode
from .htmnodes import HTMLNode

# ---------------------------------------------------------------------------


class HTMLHeadNode(HTMLNode):
    """Convenient class to represent the head node of an HTML tree.

    Children of a "head" node are limited to the ones of HEAD_TAGS list.

    """

    def __init__(self, parent):
        """Create the head node."""
        super(HTMLHeadNode, self).__init__(parent, "head", "head")

    # -----------------------------------------------------------------------
    # Invalidate some of the Node methods.
    # -----------------------------------------------------------------------

    def append_child(self, node) -> None:
        """Append a child node.

        :param node: (Node)
        :raises: NodeChildTagError: if invalid child tag (not in HEAD_TAGS list)

        """
        if node.tag not in HEAD_TAGS:
            raise NodeChildTagError(node.tag)
        HTMLNode.append_child(self, node)

    # -----------------------------------------------------------------------

    def insert_child(self, pos, node) -> None:
        """Insert a child node at the given index.

        :param pos: (int) Index position
        :param node: (Node)

        """
        if node.tag not in HEAD_TAGS:
            raise NodeChildTagError(node.tag)
        HTMLNode.insert_child(self, pos, node)

    # -----------------------------------------------------------------------
    # Add convenient methods to manage the head
    # -----------------------------------------------------------------------

    def title(self, title) -> None:
        """Set the title to the header.

        :param title: (str) The page title (expected short!)

        """
        for child in self._children:
            if child.identifier == "title":
                child.set_value(title)
                break

    # -----------------------------------------------------------------------

    def meta(self, metadict) -> None:
        """Append a new meta tag to the header.

        :param metadict: (dict)

        """
        if isinstance(metadict, dict) is False:
            raise TypeError("Expected a dict.")

        child_node = EmptyNode(self.identifier, None, "meta", attributes=metadict)
        self._children.append(child_node)

    # -----------------------------------------------------------------------

    def link(self, rel: str, href: str, link_type: str = None) -> None:
        """Add a link tag to the header.

        :param rel: (str)
        :param href: (str) Path and/or name of the link reference
        :param link_type: (str) Mimetype of the link file

        """
        d = dict()
        d["rel"] = rel

        if len(href) > 0 and href[0].isalpha():
            d["href"] = os.sep + href
        else:
            d["href"] = href

        if link_type is not None:
            d["type"] = link_type
        child_node = EmptyNode(self.identifier, None, "link", attributes=d)
        self._children.append(child_node)

    # -----------------------------------------------------------------------

    def script(self, src, script_type) -> None:
        """Add a meta tag to the header.

        :param src: (str) Script source file or Script content
        :param script_type: (str) Script type or None if script content

        """
        if script_type is not None:
            d = dict()
            d["type"] = script_type

            if len(src) > 0 and src[0].isalpha():
                d["src"] = os.sep + src
            else:
                d["src"] = src

            child_node = HTMLNode(self.identifier, None, "script", attributes=d)
            self._children.append(child_node)
        else:
            child_node = HTMLNode(self.identifier, None, "script", value=str(src))
            self._children.append(child_node)

    # -----------------------------------------------------------------------

    def css(self, css_content) -> None:
        """Append css style content.

        :param script_content: (str) CSS content

        """
        child_node = HTMLNode(self.identifier, None, "style", value=str(css_content))
        self._children.append(child_node)

# ---------------------------------------------------------------------------


class HTMLHeaderNode(HTMLNode):
    """Convenient class to represent the header node of an HTML tree.

    """
    def __init__(self, parent):
        """Create the main node.

        """
        super(HTMLHeaderNode, self).__init__(parent, "body_header", "header")

# ---------------------------------------------------------------------------


class HTMLNavNode(HTMLNode):
    """Convenient class to represent the nav node of an HTML tree.

    """
    def __init__(self, parent):
        """Create the nav node."""
        super(HTMLNavNode, self).__init__(parent, "body_nav", "nav")

# ---------------------------------------------------------------------------


class HTMLMainNode(HTMLNode):
    """Convenient class to represent the main node of an HTML tree.

    """
    def __init__(self, parent):
        """Create the main node."""
        super(HTMLMainNode, self).__init__(parent, "body_main", "main")

# ---------------------------------------------------------------------------


class HTMLFooterNode(HTMLNode):
    """Convenient class to represent the footer node of an HTML tree.

    """

    def __init__(self, parent):
        """Create the footer node."""
        super(HTMLFooterNode, self).__init__(parent, "body_footer", "footer")

# ---------------------------------------------------------------------------


class HTMLScriptNode(HTMLNode):
    """Convenient class to represent the scripts node of an HTML tree."""

    def __init__(self, parent):
        """Create the script node."""
        super(HTMLScriptNode, self).__init__(parent, "body_script", "script")