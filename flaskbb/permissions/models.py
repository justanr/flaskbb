# -*- coding: utf-8 -*-
"""
    flaskbb.permissions.models
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Permissioning models for FlaskBB

    :copyright: 2018, the FlaskBB Team
    :license: BSD, see LICENSE for more details
"""


from ..extensions import db
from ..utils.database import primary_key
from .levels import PermissionLevel


class Permission(db.Model):
    __tablename__ = "permissions"

    id = primary_key()
    name = db.Column(db.Unicode(25), nullable=False, unique=True)
    description = db.Column(db.Unicode, nullable=True)
    default = db.Column(db.Enum(PermissionLevel), default=PermissionLevel.Undefined)
