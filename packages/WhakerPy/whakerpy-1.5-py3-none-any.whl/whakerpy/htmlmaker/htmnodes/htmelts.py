"""
:filename: whakerpy.htmlmaker.htmnodes.htmelts.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Node classes to generate various HTML elements.

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

from ..emptynodes import BaseTagNode
from ..emptynodes import HTMLImage
from ..htmnodes import HTMLNode

# ---------------------------------------------------------------------------


class HTMLRadioBox(HTMLNode):
    """Represent a form with one or several input of radio type.

    """

    def __init__(self, parent, identifier):
        """Create a form node."""
        attributes = dict()
        attributes['method'] = "POST"
        attributes['name'] = identifier
        attributes['id'] = identifier
        super(HTMLRadioBox, self).__init__(parent, identifier, "form", attributes=attributes)

    def append_input(self, class_name, value, text=None, checked=False):
        """Append a label tag with an input and a span.

        :param class_name: (str) Used for both the CSS class of the label and the name of the input
        :param value: (str) input value
        :param text: (str) span tag content
        :param checked: (bool)

        """
        label_attributes = dict()
        label_attributes['class'] = str(class_name)
        if "button" not in class_name:
            label_attributes['class'] = "button " + class_name
        if checked is True:
            label_attributes['class'] += " checked"

        label_node = HTMLNode(self.identifier, None, "label", attributes=label_attributes)
        self.append_child(label_node)

        input_attributes = dict()
        input_attributes['type'] = "radio"
        input_attributes['name'] = class_name
        input_attributes['value'] = value
        if checked is True:
            input_attributes['checked'] = None

        input_node = BaseTagNode(label_node.identifier, None, "input", attributes=input_attributes)
        label_node.append_child(input_node)

        if text is not None:
            span_node = HTMLNode(label_node.identifier, None, "span", value=text)
        else:
            span_node = HTMLNode(label_node.identifier, None, "span", value=value)
        label_node.append_child(span_node)

# ---------------------------------------------------------------------------


class HTMLButtonNode(HTMLNode):
    """Represent a button element.

    The set_attribute method should be overridden to check if the given key
    is in the list of accepted attributes.

    """

    def __init__(self, parent, identifier, attributes=dict()):
        """Create an input node. Default type is 'text'.

        """
        super(HTMLButtonNode, self).__init__(parent, identifier, "button", attributes=attributes)

        if "id" not in attributes:
            self.add_attribute("id", self.identifier)
        if "name" not in attributes:
            self.add_attribute("name", self.identifier)
        if "type" not in attributes:
            self.add_attribute("type", "button")

    # -----------------------------------------------------------------------

    def set_icon(self, icon, attributes=dict()):
        """Set an icon to the button from its filename.

        :param icon: (str) Name of an icon in the app.
        :param attributes: (dict).

        """
        node = HTMLImage(self.identifier, None, src=icon)
        if len(attributes) > 0:
            for key in attributes:
                node.set_attribute(key, attributes[key])
        self.append_child(node)
        return node

    # -----------------------------------------------------------------------

    def set_text(self, ident, text, attributes=dict()):
        """Set a text to the button.

        :param ident: (str) Identifier for the span text.
        :param text: (str) Button text.
        :param attributes: (dict)

        """
        node = HTMLNode(self.identifier, ident, "span", value=text, attributes=attributes)
        if ident is not None:
            node.set_attribute("id", ident)
        self.append_child(node)

        # Accessibility
        if ident is not None:
            self.set_attribute("aria-labelledby", node.identifier)
        return node
