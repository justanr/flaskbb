# -*- coding: utf-8 -*-
"""
    flaskbb.user.services.update
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    User update services.

    :copyright: (c) 2018 the FlaskBB Team.
    :license: BSD, see LICENSE for more details
"""

import attr

from ...core.exceptions import accumulate_errors
from ...core.user.update import (
    UserDetailsUpdateHandler,
    UserEmailUpdateHandler,
    UserPasswordUpdateHandler,
    UserSettingsUpdateHandler,
)
from ...utils.database import try_commit


@attr.s(cmp=False, frozen=True, repr=True, hash=False)
class DefaultDetailsUpdateHandler(UserDetailsUpdateHandler):
    """
    Validates and updates a user's details and persists the changes to the database.
    """

    db = attr.ib()
    plugin_manager = attr.ib()
    validators = attr.ib(factory=list)

    def update_details(self, user, details):
        accumulate_errors(lambda v: v.validate_details(user, details), self.validators)
        details.assign_to_user(user)
        try_commit(self.db.session, "Could not update details")
        self.plugin_manager.hook.flaskbb_details_updated(
            user=user, details_update=details
        )


@attr.s(cmp=False, frozen=True, repr=True, hash=False)
class DefaultPasswordUpdateHandler(UserPasswordUpdateHandler):
    """
    Validates and updates a user's password and persists the changes to the database.
    """

    db = attr.ib()
    plugin_manager = attr.ib()
    validators = attr.ib(factory=list)

    def update_password(self, user, password_change):
        accumulate_errors(
            lambda v: v.validate_password(user, password_change), self.validators
        )
        user.password = password_change.new_password
        try_commit(self.db.session, "Could not update password")
        self.plugin_manager.hook.flaskbb_password_updated(user=user)


@attr.s(cmp=False, frozen=True, repr=True, hash=False)
class DefaultEmailUpdateHandler(UserEmailUpdateHandler):
    """
    Validates and updates a user's email and persists the changes to the database.
    """

    db = attr.ib()
    plugin_manager = attr.ib()
    validators = attr.ib(factory=list)

    def update_email(self, user, email_update):
        accumulate_errors(
            lambda v: v.validate_email(user, email_update), self.validators
        )
        user.email = email_update.new_email
        try_commit(self.db.session, "Could not update email")
        self.plugin_manager.hook.flaskbb_email_updated(
            user=user, email_update=email_update
        )


@attr.s(cmp=False, frozen=True, repr=True, hash=False)
class DefaultSettingsUpdateHandler(UserSettingsUpdateHandler):
    """
    Updates a user's settings and persists the changes to the database.
    """

    db = attr.ib()
    plugin_manager = attr.ib()

    def update_settings(self, user, settings_update):
        settings_update.assign_to_user(user)
        try_commit(self.db.session, "Could not update settings")
        self.plugin_manager.hook.flaskbb_settings_updated(
            user=user, settings_update=settings_update
        )
