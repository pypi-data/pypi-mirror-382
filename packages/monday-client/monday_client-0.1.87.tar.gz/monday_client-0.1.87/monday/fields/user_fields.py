# This file is part of monday-client.
#
# Copyright (C) 2024 Leet Cyber Security <https://leetcybersecurity.com/>
#
# monday-client is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# monday-client is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with monday-client. If not, see <https://www.gnu.org/licenses/>.

"""
Module containing predefined field sets for monday.com user operations.

This module provides a collection of commonly used field combinations when
querying monday.com users, making it easier to maintain consistent field
sets across user operations.
"""

from monday.fields.base_fields import BaseFields
from monday.services.utils.fields import Fields


class UserFields(BaseFields):
    """
    Collection of predefined field sets for user operations.

    See Also:
        `monday.com API User fields <https://developer.monday.com/api-reference/reference/users#fields>`_

    """

    BASIC = Fields('id email')
    """
    Returns the following fields:

    - id: User's ID
    - email: User's email
    """
