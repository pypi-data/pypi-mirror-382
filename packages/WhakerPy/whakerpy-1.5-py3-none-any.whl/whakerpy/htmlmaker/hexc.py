"""
:filename: whakerpy.htmlmaker.hexc.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Exception classes to be used in htmlmaker package.

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

from whakerpy.messages import error

# -----------------------------------------------------------------------


class NodeTypeError(TypeError):
    """:ERROR 9110:.

    {!s:s} is not of the expected type 'HTMLNode'.

    """

    def __init__(self, rtype):
        self._status = 9110
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(rtype)

    def __str__(self):
        return repr(self.parameter)

    def get_status(self):
        return self._status

    status = property(get_status, None)

# -----------------------------------------------------------------------


class NodeInvalidIdentifierError(ValueError):
    """:ERROR 9310:.

    Invalid HTML node identifier '{!s:s}'.

    """

    def __init__(self, value):
        self._status = 9310
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(value)

    def __str__(self):
        return repr(self.parameter)

    def get_status(self):
        return self._status

    status = property(get_status, None)

# -----------------------------------------------------------------------


class NodeIdentifierError(KeyError):
    """:ERROR 9410:.

    Expected HTML node identifier {:s}. Got '{!s:s}' instead.

    """

    def __init__(self, expected, value):
        self._status = 9410
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(expected, value)

    def __str__(self):
        return repr(self.parameter)

    def get_status(self):
        return self._status

    status = property(get_status, None)

# -----------------------------------------------------------------------


class NodeParentIdentifierError(ValueError):
    """:ERROR 9312:.

    Expected HTML Parent node identifier {:s}. Got '{!s:s}' instead.

    """

    def __init__(self, expected, value):
        self._status = 9312
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(expected, value)

    def __str__(self):
        return repr(self.parameter)

    def get_status(self):
        return self._status

    status = property(get_status, None)

# -----------------------------------------------------------------------


class NodeTagError(ValueError):
    """:ERROR 9320:.

    Invalid HTML node tag '{!s:s}'.

    """

    def __init__(self, value):
        self._status = 9320
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(value)

    def __str__(self):
        return repr(self.parameter)

    def get_status(self):
        return self._status

    status = property(get_status, None)

# -----------------------------------------------------------------------


class NodeChildTagError(ValueError):
    """:ERROR 9325:.

    Invalid HTML child node tag '{!s:s}'.

    """

    def __init__(self, value):
        self._status = 9325
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(value)

    def __str__(self):
        return repr(self.parameter)

    def get_status(self):
        return self._status

    status = property(get_status, None)

# -----------------------------------------------------------------------


class NodeAttributeError(ValueError):
    """:ERROR 9330:.

    Invalid HTML node attribute '{!s:s}'.

    """

    def __init__(self, value):
        self._status = 9330
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(value)

    def __str__(self):
        return repr(self.parameter)

    def get_status(self):
        return self._status

    status = property(get_status, None)

# -----------------------------------------------------------------------


class NodeKeyError(KeyError):
    """:ERROR 9400:.

    Invalid node '{!s:s}' for data '{!s:s}'.

    """

    def __init__(self, data_name, value):
        self._status = 9400
        self.parameter = error(self._status) + \
                         (error(self._status, "globals")).format(value, data_name)

    def __str__(self):
        return repr(self.parameter)

    def get_status(self):
        return self._status

    status = property(get_status, None)
