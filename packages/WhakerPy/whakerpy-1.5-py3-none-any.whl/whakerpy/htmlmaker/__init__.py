"""
:filename: whakerpy.htmlmaker.__init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: A tree representation of HTML.

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

from .hconsts import HTML_EMPTY_TAGS
from .hconsts import HTML_TAGS
from .hconsts import HTML_GLOBAL_ATTR
from .hconsts import HTML_VISIBLE_ATTR
from .hconsts import HTML_TAG_ATTR
from .hconsts import ARIA_TAG_ATTR

from .hexc import NodeTypeError
from .hexc import NodeTagError
from .hexc import NodeKeyError
from .hexc import NodeAttributeError
from .hexc import NodeChildTagError
from .hexc import NodeInvalidIdentifierError
from .hexc import NodeIdentifierError
from .hexc import NodeParentIdentifierError

from .basenodes import BaseNode
from .basenodes import Doctype
from .basenodes import HTMLComment

from .emptynodes import BaseTagNode
from .emptynodes import EmptyNode
from .emptynodes import HTMLImage
from .emptynodes import HTMLInputText
from .emptynodes import HTMLHr
from .emptynodes import HTMLBr

from .htmnodes import HTMLNode
from .htmnodes import HTMLRadioBox
from .htmnodes import HTMLButtonNode

from .treeelts import HTMLHeadNode
from .treeelts import HTMLHeaderNode
from .treeelts import HTMLNavNode
from .treeelts import HTMLMainNode
from .treeelts import HTMLFooterNode
from .treeelts import HTMLScriptNode

from .treenode import HTMLTree
from .treeerror import HTMLTreeError

__all__ = (
    "HTML_EMPTY_TAGS",
    "HTML_TAGS",
    "HTML_VISIBLE_ATTR",
    "HTML_GLOBAL_ATTR",
    "HTML_TAG_ATTR",
    "ARIA_TAG_ATTR",
    "NodeTypeError",
    "NodeTagError",
    "NodeKeyError",
    "NodeAttributeError",
    "NodeChildTagError",
    "NodeInvalidIdentifierError",
    "NodeIdentifierError",
    "NodeParentIdentifierError",
    "Doctype",
    "HTMLComment",
    "HTMLImage",
    "HTMLHr",
    "HTMLBr",
    "HTMLInputText",
    "HTMLRadioBox",
    "HTMLButtonNode",
    "BaseNode",
    "BaseTagNode",
    "EmptyNode",
    "HTMLNode",
    "HTMLHeadNode",
    "HTMLHeaderNode",
    "HTMLNavNode",
    "HTMLMainNode",
    "HTMLFooterNode",
    "HTMLScriptNode",
    "HTMLTree",
    "HTMLTreeError"
)
