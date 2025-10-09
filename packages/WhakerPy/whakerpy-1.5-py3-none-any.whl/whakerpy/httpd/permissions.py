"""
:filename: whakerpy.webapp.permissions.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Check file permissions.

.. _This file is part of WhakerPy: https://whakerpy.sourceforge.io
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

import re
import os
import stat
try:
    import grp
except ImportError:
    # grp will be None if the module is unavailable
    grp = None

# ---------------------------------------------------------------------------


class UnixPermissions:
    """Class to handle Unix file permission roles (owner, group, others).

    :example:
    >>> permissions = UnixPermissions()
    >>> "owner" in permissions
    True

    """
    # Protected list of Unix permissions roles
    __VALID_ROLES = ["owner", "group", "others"]

    # -----------------------------------------------------------------------

    @classmethod
    def is_valid_role(cls, role: str) -> bool:
        """Check if the provided role is valid.

        :param role: (str) The role to check among the valid roles.

        """
        return role in cls.__VALID_ROLES

    # -----------------------------------------------------------------------

    @property
    def owner(self):
        """Return the 'owner' role."""
        return "owner"

    @property
    def group(self):
        """Return the 'group' role."""
        return "group"

    @property
    def others(self):
        """Return the 'others' role."""
        return "others"

    # -----------------------------------------------------------------------

    def __iter__(self):
        """Allow iteration over VALID_ROLES."""
        return iter(self.__VALID_ROLES)

    # -----------------------------------------------------------------------

    def __enter__(self):
        """Enter the context: Initialize or lock resources if needed."""
        # Return the object to use inside the 'with' block
        return self

    # -----------------------------------------------------------------------

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the context: Clean up resources or handle exceptions.

        """
        # Return False to propagate exceptions
        return False

# ---------------------------------------------------------------------------


class FileAccessChecker:
    """Specialized class for checking file permissions on a specified file.

    This class provides methods to check if a user, group, or owner has specific
    access rights to a given file, such as read permissions.

    Available only for UNIX-based platforms. Instantiating the class on another
    platform raises an EnvironmentError.

    :example:
    >>> checker = FileAccessChecker('/path/to/file')
    >>> checker.read_allowed(who='owner')
    True
    >>> checker.read_allowed(who='group')
    False

    """

    def __init__(self, filename: str):
        """Initialize the FileAccessChecker with a specific file.

        The initialization ensures that the system supports group-related
        functionalities by checking for the availability of the 'grp' module.

        :param filename: (str) Path to the file to check.
        :raises: EnvironmentError: If 'grp' module is not available (invalid platform)
        :raises: FileNotFoundError: If the file does not exist.

        """
        if grp is None:
            raise EnvironmentError("The 'grp' module is not available on this platform.")
        self.__filename = filename

        # Check if the file exists, raise an error if not
        if os.path.exists(self.__filename) is False:
            raise FileNotFoundError(f"File not found: {self.__filename}")

        # Get the file's status
        self.__file_stat = os.stat(self.__filename)

    # -----------------------------------------------------------------------

    def get_filename(self):
        """Return the examined filename."""
        return self.__filename

    # -----------------------------------------------------------------------

    def read_allowed(self, who: str = "others") -> bool:
        """Check if the given persons have read permission on the file.

        "who" is one of the UnixPermission() or a comibation with '&' or '|'
        (but not both). For example 'group&others' checks if both group
        and others have read access; 'owner|group' checks if either owner
        or group has read access; 'owner&group&others' checks if all have
        read access. Forbidden combination is for example:
        'owner&group|others'

        :param who: (str) Can be 'others', 'group', or 'owner', or a combination.
        :return: (bool) True if read permission is granted, False otherwise.
        :raises: ValueError: If 'who' contains invalid roles or syntax.

        """
        # Validate the 'who' parameter using UnixPermissions
        with UnixPermissions() as permissions:
            # Extract individual roles from the expression using a regex (roles must be in UnixPermissions)
            valid_roles = list(permissions)
            role_pattern = "|".join(re.escape(role) for role in valid_roles)
            expression_pattern = rf"^\s*({role_pattern})(\s*[\&\|]\s*({role_pattern}))*\s*$"

            if not re.match(expression_pattern, who):
                raise ValueError(f"Invalid 'who' value or syntax: {who}. "
                                 f"Must contain only {valid_roles} with '&' or '|'.")

        # Check if the expression contains both '&' and '|', which is forbidden
        if '&' in who and '|' in who:
            raise ValueError("Combination of '&' and '|' is forbidden in the 'who' parameter.")

        # Split by '|' to evaluate the 'OR' conditions first
        or_conditions = who.split('|')

        for or_condition in or_conditions:
            # Split by '&' to evaluate the 'AND' conditions within each OR block
            and_roles = or_condition.split('&')

            # Check if all roles within the 'AND' block have permission
            if all(self.__check_permission_for_role(role.strip()) for role in and_roles):
                return True  # Return True if all roles in the 'AND' condition have permission

        return False  # Return False if no condition is satisfied

    # -----------------------------------------------------------------------

    def __check_permission_for_role(self, role: str) -> bool:
        """Helper function to check permissions for a single role.

        :param role: (str) Who to check permissions for: 'others', 'group', or 'owner'.

        """
        current_uid = os.geteuid()  # Effective user ID of the current process
        current_gid = os.getegid()  # Effective group ID of the current process

        # Check owner, group, and others' permissions
        mode = self.__file_stat.st_mode
        owner_uid = self.__file_stat.st_uid
        group_gid = self.__file_stat.st_gid

        # Determine read permission based on the role
        if role == "owner" and current_uid == owner_uid:
            return bool(mode & stat.S_IRUSR)  # Owner read permission
        elif role == "group" and current_gid == group_gid:
            return bool(mode & stat.S_IRGRP)  # Group read permission
        elif role == "others":
            return bool(mode & stat.S_IROTH)  # Others' read permission
        return False

