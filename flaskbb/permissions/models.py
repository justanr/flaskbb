# -*- coding: utf-8 -*-
"""
    flaskbb.permissions.models
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Permissioning models for FlaskBB

    :copyright: 2018, the FlaskBB Team
    :license: BSD, see LICENSE for more details
"""


from sqlalchemy.ext.declarative import declared_attr

from ..extensions import db
from ..utils.database import primary_key
from .levels import PermissionLevel


class Permission(db.Model):
    __tablename__ = "permissions"

    id = primary_key()
    name = db.Column(db.Unicode(25), nullable=False, unique=True)
    description = db.Column(db.Unicode, nullable=True)
    default = db.Column(db.Enum(PermissionLevel), default=PermissionLevel.Undefined)


class PermissionBase(object):
    id = primary_key()
    value = db.Column(
        db.Enum(PermissionLevel), default=PermissionLevel.Undefined, nullable=False
    )

    when_moderator = db.Column(db.Boolean(), default=False, nullable=False)

    @declared_attr
    def permission_id(cls):
        return db.Column(db.ForeignKey("permissions.id"), nullable=False)

    @declared_attr
    def permission(cls):
        return db.relationship("Permission", uselist=False, lazy="joined")


class HasPermissions(object):

    @declared_attr
    def permissions_(cls):
        perms_name = "{}Permission".format(cls.__name__)
        table_name = "{}_permissions".format(cls.__tablename__)
        parent_id = db.Column(
            db.ForeignKey("{}.id".format(cls.__tablename__)), nullable=False
        )

        def repr(self):
            return "<{}Permission {} value={}>".format(
                cls.__name__, self.permission.name, self.value
            )

        cls.Permission = type(
            perms_name,
            (PermissionBase, db.Model),
            {"parent_id": parent_id, "__tablename__": table_name, "__repr__": repr},
        )

        return db.relationship(cls.Permission, backref="parent", lazy="joined")
