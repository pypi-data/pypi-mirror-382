# -*- coding: UTF-8 -*-
"""
:filename: whakerpy.messages.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Manage the messages of the application in SPPAS style.

.. _This file is part of WhakerPy: https://whakerpy.sourceforge.io
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

MESSAGES = dict()
MESSAGES[377] = "Invalid HTTPD status code value '{!s:s}'."
MESSAGES[9110] = "{!s:s} is not of the expected type 'HTMLNode'."
MESSAGES[9310] = "Invalid HTML node identifier '{!s:s}'."
MESSAGES[9312] = "Expected HTML Parent node identifier {:s}. Got '{!s:s}' instead."
MESSAGES[9320] = "Invalid HTML node tag '{!s:s}'."
MESSAGES[9325] = "Invalid HTML child node tag '{!s:s}'."
MESSAGES[9330] = "Invalid HTML node attribute '{!s:s}'."
MESSAGES[9400] = "Invalid node '{!s:s}' for data '{!s:s}'."
MESSAGES[9410] = "Expected HTML node identifier {:s}. Got '{!s:s}' instead."

# ---------------------------------------------------------------------------


def error(msg_id, domain=None):
    """Return the error message of given ID.

    :param msg_id: (str | int) Error ID
    :param domain: Unused.

    """
    # Format the input message
    if isinstance(msg_id, int):
        msg = "{:04d}".format(msg_id)
    else:
        msg = str(msg_id)
    msg = ":ERROR " + msg + ": "

    if msg_id in MESSAGES.keys():
        return msg + MESSAGES[msg_id]

    return msg
