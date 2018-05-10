# -*- coding: utf-8 -*-
"""
    flaskbb.permissions.levels
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Permissioning levels for FlaskBB

    :copyright: 2018, the FlaskBB Team
    :license: BSD, see LICENSE for more details
"""

from enum import IntEnum


class PermissionLevel(IntEnum):
    Undefined = 0
    No = 1
    Yes = 2
    Never = 3
    Always = 4

    def __bool__(self):
        return self == PermissionLevel.Yes or self == PermissionLevel.Always

    __nonzero__ = __bool__
