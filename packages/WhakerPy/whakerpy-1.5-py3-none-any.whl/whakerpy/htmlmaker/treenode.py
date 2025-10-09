"""
:filename: whakerpy.htmlmaker.treenode.py
:author: Brigitte Bigi
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

from __future__ import annotations
import os

from .hexc import NodeTypeError
from .hexc import NodeIdentifierError
from .basenodes import BaseNode
from .basenodes import Doctype
from .basenodes import HTMLComment
from .htmnodes import HTMLNode
from .treeelts import HTMLHeadNode
from .treeelts import HTMLHeaderNode
from .treeelts import HTMLNavNode
from .treeelts import HTMLMainNode
from .treeelts import HTMLFooterNode
from .treeelts import HTMLScriptNode

# ---------------------------------------------------------------------------


class HTMLTree(BaseNode):
    """Root of an HTML tree.

    Since the early days of the World Wide Web, there have been many versions:
    [source: <https://www.w3schools.com/html/html_intro.asp>]

    -    1989: 	Tim Berners-Lee invented www
    -    1991: 	Tim Berners-Lee invented HTML
    -    1993: 	Dave Raggett drafted HTML+
    -    1995: 	HTML Working Group defined HTML 2.0
    -    1997: 	W3C Recommendation: HTML 3.2
    -    1999: 	W3C Recommendation: HTML 4.01
    -    2000: 	W3C Recommendation: XHTML 1.0
    -    2008: 	WHATWG HTML5 First Public Draft
    -    2012: 	WHATWG HTML5 Living Standard
    -    2014: 	W3C Recommendation: HTML5
    -    2016: 	W3C Candidate Recommendation: HTML 5.1
    -    2017: 	W3C Recommendation: HTML5.1 2nd Edition
    -    2017: 	W3C Recommendation: HTML5.2

    HTML elements are generally made of a start tag, an optional element
    content, and an end tag. However, several elements have only a start
    tag, like "br" or "img", and a few elements don't have tag at all,
    like comments.

    An HTMLTree has two children: a doctype node, and a "html" node.
    The "html" tag is the container for all HTML elements of the page.
    The following properties allow to access to "html" children nodes:

    - head
    - body_header
    - body_nav
    - body_main
    - body_footer
    - body_script

    :example:
    >>> # Create the tree
    >>> htree = HTMLTree("index")
    >>> htree.add_html_attribute("lang", "en")
    >>> # Fill in the <head> element node with:
    >>> # a title, a meta and a link
    >>> htree.head.title("Purpose")
    >>> htree.head.meta({"charset": "utf-8"})
    >>> htree.head.link(rel="icon", href="/static/favicon.ico")
    >>> # Fill in the <body> element node with:
    >>> # A <nav> tag in the header, a <h1> tag in the body and a <p> tag in the footer
    >>> htree.set_body_attribute("class", "colors_scheme_dark")
    >>> nav = HTMLNode(htree.body_header.identifier, "navmenu", "nav")
    >>> htree.body_header.append_child(nav)
    >>> node = HTMLNode(htree.body_main.identifier, None, "h1", value="this is a title")
    >>> htree.body_main.append_child(node)
    >>> node = HTMLNode(htree.body_footer.identifier, None, "p", value="&copy; me now")
    >>> htree.body_footer.append_child(node)
    >>> # Save into a file
    >>> htree.serialize_to_file("/path/to/file.html")

    This class does not support yet the global attributes -- i.e. attributes
    that can be used with all HTML elements.
    See <https://www.w3schools.com/TAgs/ref_standardattributes.asp>

    """

    def __init__(self, identifier: str):
        """Create the tree root and children nodes.

        The created tree matches the HTML5 recommendations for the document
        structure. The HTML tree has 2 children: a doctype and an HTML element.
        The HTML node has 2 children: the "head" and the "body". The body
        has 5 children: "header", "nav", "main", "footer", "script".
        The empty nodes are not serialized.

        :param identifier: (str) An identifier for the tree node.

        """
        super(HTMLTree, self).__init__(parent=None, identifier=identifier)

        # The HTML tree has 2 children: a doctype and an HTML element.
        self.__doctype = Doctype()
        self.__html = HTMLNode(identifier, None, "html")

        # The HTML node has 2 children: the <head> and the <body> (public)
        self.__html.append_child(HTMLHeadNode(self.__html.identifier))
        body = HTMLNode(self.__html.identifier, "body", "body")
        self.__html.append_child(body)

        # The 5 default HTML body children. 
        body.append_child(HTMLHeaderNode(body.identifier))
        body.append_child(HTMLNavNode(body.identifier))
        body.append_child(HTMLMainNode(body.identifier))
        body.append_child(HTMLFooterNode(body.identifier))
        body.append_child(HTMLScriptNode(body.identifier))

    # -----------------------------------------------------------------------
    # Override base class.
    # -----------------------------------------------------------------------

    def set_parent(self, node_id: str) -> None:
        """Override. Do not set the parent identifier. """
        return None

    # -----------------------------------------------------------------------

    def is_leaf(self) -> bool:
        """Override. Return False. """
        return False

    # -----------------------------------------------------------------------
    # Public access to the html attributes and to the children.
    # -----------------------------------------------------------------------

    def add_html_attribute(self, key: str, value: str) -> None:
        """Add or append a property to the HTML node.

        :param key: (str) Key property of an HTML attribute
        :param value: (str) Value of the attribute

        :Raises: NodeTypeError: if key or value is not a string
        :Raises: NodeAttributeError: if unknown key.

        """
        self.__html.add_attribute(key, value)

    # -----------------------------------------------------------------------

    def get_body_attribute_value(self, key: str) -> str:
        """Get the attribute value of the body element node.

        :param key: (str) Key property of an HTML attribute
        :return: (str) The attribute value of the <body> element

        """
        return self._get_body().get_attribute_value(key)

    # -----------------------------------------------------------------------

    def add_body_attribute(self, key: str, value: str) -> str:
        """Add an attribute to the body element node.

        :param key: (str) Key property of an HTML attribute
        :param value: (str) Value of the attribute
        :Raises: NodeTypeError: if key or value is not a string
        :raises: NodeAttributeError: if unknown key
        :return: normalized key

        """
        return self._get_body().add_attribute(key, value)

    # -----------------------------------------------------------------------

    def set_body_attribute(self, key: str, value: str) -> None:
        """Set an attribute of the body.

        :param key: (str) Key property of an HTML attribute
        :param value: (str) Value of the attribute
        :return: (bool) The attribute is set

        """
        self._get_body().set_attribute(key, value)

    # -----------------------------------------------------------------------

    def get_body_identifier(self) -> str:
        """Return the identifier of the body node.

        :return: (str) the identifier of the body node.

        """
        return self._get_body().identifier

    # -----------------------------------------------------------------------

    def insert_body_child(self, child: HTMLNode, index: int = 0) -> None:
        """Insert a html node in the body.

        :param child: (HTMLNode) the node to append in the body
        :param index: (int) Optional, the index where insert the child, by default the index is set to 0

        :raises ValueError: If the index is negative

        """
        if index < 0:
            raise ValueError("The index can't be negative !")

        self._get_body().insert_child(index, child)

    # -----------------------------------------------------------------------

    def get_head(self) -> HTMLNode:
        """Get the head node element.

        :return: (HTMLNode) Head node element

        """
        return self.__html.get_child("head")

    # -----------------------------------------------------------------------

    def set_head(self, head_node: HTMLNode) -> None:
        """Replace the current head node by the given one.

        :param head_node: (HTMLNode)

        :Raises: NodeTypeError: if head_node is not an HTMLNode
        :raises: NodeIdentifierError: if head_node identifier is not "head"

        """
        # if isinstance(head_node, HTMLNode) is False:
        if hasattr(head_node, 'identifier') is False:
            raise NodeTypeError(type(head_node))
        if head_node.identifier != "head":
            raise NodeIdentifierError("head", head_node.identifier)
        head_node.set_parent(self.__html.identifier)
        self.__html.remove_child("head")
        self.__html.insert_child(0, head_node)

    # head node element of the HTMLTree.
    head = property(get_head, set_head)

    # -----------------------------------------------------------------------

    def get_body_header(self) -> HTMLNode | None:
        """Get the body->header element node.

        :return: (HTMLNode | None) Body header node element

        """
        return self._get_body().get_child("body_header")

    # -----------------------------------------------------------------------

    def set_body_header(self, body_node):
        """Replace the current body->header element node by the given one.

        :param body_node: (HTMLNode)

        :Raises: NodeTypeError: if head_node is not an HTMLNode
        :Raises: NodeIdentifierError: if head_node identifier is not "body_header"

        """
        # if isinstance(body_node, HTMLNode) is False:
        if hasattr(body_node, 'identifier') is False:
            raise NodeTypeError(type(body_node))
        if body_node.identifier != "body_header":
            raise NodeIdentifierError("body_header", body_node.identifier)
        body_node.set_parent(self._get_body().identifier)
        self._get_body().remove_child("body_header")
        self._get_body().insert_child(0, body_node)

    body_header = property(get_body_header, set_body_header)

    # -----------------------------------------------------------------------

    def get_body_nav(self):
        """Get the body->nav element node.

        :return: (HTMLNode) Body nav node element

        """
        return self._get_body().get_child("body_nav")

    # -----------------------------------------------------------------------

    def set_body_nav(self, body_node):
        """Replace the current body->nav node by the given one.

        :param body_node: (HTMLNode)

        :Raises: NodeTypeError: if head_node is not an HTMLNode
        :raises: NodeIdentifierError: if head_node identifier is not "body_nav"

        """
        #if isinstance(body_node, HTMLNode) is False:
        if hasattr(body_node, 'identifier') is False:
            raise NodeTypeError(type(body_node))
        if body_node.identifier != "body_nav":
            raise NodeIdentifierError("body_nav", body_node.identifier)
        body_node.set_parent(self._get_body().identifier)
        self._get_body().remove_child("body_nav")
        self._get_body().insert_child(1, body_node)

    body_nav = property(get_body_nav, set_body_nav)

    # -----------------------------------------------------------------------

    def get_body_main(self):
        """Get the body->main element node.

        :return: (HTMLNode) Body main node element

        """
        return self._get_body().get_child("body_main")

    body_main = property(get_body_main, None)

    # -----------------------------------------------------------------------

    def get_body_footer(self):
        """Get the body->footer element node.

        :return: (HTMLNode) Body footer node element

        """
        return self._get_body().get_child("body_footer")

    # -----------------------------------------------------------------------

    def set_body_footer(self, body_node):
        """Replace the current body->footer node by the given one.

        :param body_node: (HTMLNode)
        :Raises: NodeTypeError: if head_node is not an HTMLNode
        :Raises: NodeIdentifierError: if head_node identifier is not "body_footer"

        """
        #if isinstance(body_node, HTMLNode) is False:
        if hasattr(body_node, 'identifier') is False:
            raise NodeTypeError(type(body_node))
        if body_node.identifier != "body_footer":
            raise NodeIdentifierError("body_footer", body_node.identifier)
        body_node.set_parent(self._get_body().identifier)
        self._get_body().remove_child("body_footer")
        self._get_body().append_child(body_node)

    body_footer = property(get_body_footer, set_body_footer)

    # -----------------------------------------------------------------------

    def get_body_script(self):
        """Get the body->script element node.

        :return: (HTMLNode) Body script node element

        """
        return self._get_body().get_child("body_script")

    # -----------------------------------------------------------------------

    def set_body_script(self, body_node):
        """Replace the current body->script node by the given one.

        :param body_node: (HTMLNode)

        :Raises: NodeTypeError: if head_node is not an HTMLNode
        :raises: NodeIdentifierError: if head_node identifier is not "body_script"

        """
        #if isinstance(body_node, HTMLNode) is False:
        if hasattr(body_node, 'identifier') is False:
            raise NodeTypeError(type(body_node))
        if body_node.identifier != "body_script":
            raise NodeIdentifierError("body_script", body_node.identifier)
        body_node.set_parent(self._get_body().identifier)
        self._get_body().remove_child("body_script")
        self._get_body().append_child(body_node)

    body_script = property(get_body_script, set_body_script)

    # -----------------------------------------------------------------------

    def _get_body(self) -> HTMLNode:
        """Get the body element node.

        :return: (HTMLNode) The body element node

        """
        return self.__html.get_child("body")

    # -----------------------------------------------------------------------
    # Convenient methods to add an HTML node in the body part of the tree
    # -----------------------------------------------------------------------

    def comment(self, content):
        """Add a comment to the body->main."""
        node = HTMLComment(self.body_main.identifier, content)
        self.body_main.append_child(node)
        return node

    # -----------------------------------------------------------------------

    def element(self, tag: str = "div", ident=None, class_name=None) -> HTMLNode:
        """Add a node to the body->main.

        :param tag: (str) HTML element name
        :param ident: (str) Identifier of the element
        :param class_name: (str) Value of the class attribute
        :return: (HTMLNode) The created node

        """
        att = dict()
        if ident is not None:
            att["id"] = str(ident)
        if class_name is not None:
            att["class"] = str(class_name)

        node = HTMLNode(self.body_main.identifier, ident, tag, attributes=att)
        self.body_main.append_child(node)
        return node

    # -----------------------------------------------------------------------

    def button(self, value: str, on_clik: str, identifier: str = None, class_name: str = None) -> HTMLNode:
        """Add a classic button with given text value and onclick event to the body->main.

        :param value: (str) The text write in the button
        :param on_clik: (str) the onclick event of the button (generally call a js function)
        :param identifier: (str) Optional, the identifier of the node (and also the id of the tag in the html generated)
        :param class_name: (str) Optional, the classes attribute for css of the button tag

        :return: (HTMLNode) The button node created

        """
        attributes = {'onclik': on_clik}

        if identifier is not None:
            attributes['id'] = identifier
        if class_name is not None:
            attributes['class'] = class_name

        button = HTMLNode(self.body_main.identifier, identifier, "button", value=value, attributes=attributes)
        self.body_main.append_child(button)
        return button

    # -----------------------------------------------------------------------

    def image(self, src: str, alt_text: str, identifier: str = None, class_name: str = None) -> HTMLNode:
        """Add an image to the body->main.

        :param src: (str) The path of the image file
        :param alt_text: (str) the alternative text if for some reason the image doesn't display or for narrator
        :param identifier: (str) Optional, the identifier of the node (and also the id of the tag in the html generated)
        :param class_name: (str) Optional, the classes attribute for css of the button tag

        :return: (HTMLNode) The image node created

        """
        attributes = {
            'src': src,
            'alt': alt_text
        }

        if identifier is not None:
            attributes['id'] = identifier
        if class_name is not None:
            attributes['class'] = class_name

        img = HTMLNode(self.body_main.identifier, identifier, "img", attributes=attributes)
        self.body_main.append_child(img)
        return img

    # -----------------------------------------------------------------------
    # Convenient methods to add elements in the head
    # -----------------------------------------------------------------------

    def set_title(self, entry):
        self.head.title(entry)

    def add_meta(self, metadict):
        self.head.meta(metadict)

    def add_link(self, rel, href, link_type=None):
        self.head.link(rel, href, link_type)

    def add_css(self, filename):
        with open(filename) as f:
            content = f.readlines()
        self.head.css("\n".join(content))

    def add_css_link(self, href):
        self.head.link("stylesheet", href, link_type="text/css")

    def add_script(self, script: str, script_type: str = "application/javascript"):
        script = HTMLNode(self.head.identifier, None, "script", value=script, attributes={'type': script_type})
        self.head.append_child(script)

    def add_script_file(self, script: str, script_type: str = "application/javascript"):
        self.head.script(script, script_type=script_type)

    # -----------------------------------------------------------------------
    # Serialize HTML
    # -----------------------------------------------------------------------

    @staticmethod
    def serialize_element(node: HTMLNode, nbs: int = 4) -> str:
        """Serialize an element node only if not empty.

        :param node: (HTMLNode) Any element node
        :param nbs: (int) Number of space for indentation
        :raises: NodeTypeError: If the given parameter is not an HTMLNode
        :return: (str) Serialized node only if it has children or a value.

        """
        if node is None:
            return ""
        # if isinstance(node, HTMLNode) is False:
        if hasattr(node, 'identifier') is False:
            raise NodeTypeError(type(node))

        if node.children_size() > 0 or node.get_value() is not None:
            return node.serialize(nbs)
        return ""

    # -----------------------------------------------------------------------

    def serialize(self, nbs: int = 4) -> str:
        """Override. Serialize the tree into HTML.

        :param nbs: (int) Number of spaces for the indentation
        :return: (str)

        """
        s = self.__doctype.serialize()
        s += "<html"
        for akey in self.__html.get_attribute_keys():
            avalue = self.__html.get_attribute_value(akey)
            s += " " + akey
            if avalue is not None:
                s += '="' + avalue + '"'
        s += ">\n"
        s += self.__html.get_child("head").serialize(nbs)

        s += "<body"
        for akey in self._get_body().get_attribute_keys():
            avalue = self._get_body().get_attribute_value(akey)
            s += " " + akey
            if avalue is not None:
                s += '="' + avalue + '"'
        s += ">\n"

        # It should be "s += self.__html.get_child("body").serialize(nbs)"
        # but the tree has main then header then nav then footer!
        if self.get_body_header() is not None:
            s += self.serialize_element(self.get_body_header(), nbs)
        if self.get_body_nav() is not None:
            s += self.serialize_element(self.get_body_nav(), nbs)
        if self.get_body_main() is not None:
            s += self.get_body_main().serialize(nbs)
        if self.get_body_footer() is not None:
            s += self.serialize_element(self.get_body_footer(), nbs)
        if self.get_body_script() is not None:
            s += self.serialize_element(self.get_body_script(), nbs)
        s += "\n</body>\n</html>\n"

        return s

    # -----------------------------------------------------------------------

    def serialize_to_file(self, filename: str, nbs: int = 4) -> str:
        """Serialize the tree into an HTML file.

        The HTML content is saved into the file and its URL is returned.

        :param filename: (str) A filename to save the serialized HTML string.
        :param nbs: (int) Number of spaces for the indentation
        :returns: (str) file URL

        """
        with open(filename, "w") as fp:
            fp.write(self.serialize(nbs))
        return "file://" + os.path.abspath(filename)

    # -----------------------------------------------------------------------
    # Overloads.
    # -----------------------------------------------------------------------

    def __contains__(self, identifier):
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def __str__(self):
        return "HTMLTree ({:s})".format(self.identifier)
