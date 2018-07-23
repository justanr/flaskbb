# -*- coding: utf-8 -*-
"""
    flaskbb.user.services.validators
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Validators for use with user services.

    :copyright: (c) 2018 the Flaskbb Team.
    :license: BSD, see LICENSE for more details
"""


import attr
from flask_babelplus import gettext as _
from requests.exceptions import RequestException
from sqlalchemy import func

from ...core.exceptions import StopValidation, ValidationError
from ...core.user.update import EmailValidator, PasswordValidator, UserDetailValidator
from ...utils.helpers import check_image


@attr.s(cmp=False, hash=False, frozen=True, repr=True)
class CantShareEmailValidator(EmailValidator):
    """
    Validates that the new email for the user isn't currently registered by
    another user.
    """
    users = attr.ib()

    def validate_email(self, user, email_update):
        others = self.users.query.filter(
            self.users.id != user.id,
            func.lower(self.users.email) == email_update.new_email,
        ).count()

        if others != 0:
            raise ValidationError(
                "new_email",
                _("%(email)s is already registered", email=email_update.new_email),
            )


class OldEmailMustMatch(EmailValidator):
    """
    Validates that the email entered by the user is the current email of the user.
    """
    def validate_email(self, user, email_update):
        if user.email != email_update.old_email:
            raise StopValidation([("old_email", _("Old email does not match"))])


class EmailsMustBeDifferent(EmailValidator):
    """
    Validates that the new email entered by the user isn't the same as the
    current email for the user.
    """
    def validate_email(self, user, email_update):
        if user.email == email_update.new_email:
            raise ValidationError("new_email", _("New email address must be different"))


class PasswordsMustBeDifferent(PasswordValidator):
    """
    Validates that the new password entered by the user isn't the same as the
    current email for the user.
    """
    def validate_password(self, user, password_change):
        if user.check_password(password_change.new_password):
            raise ValidationError("new_password", _("New password must be different"))


class OldPasswordMustMatch(PasswordValidator):
    """
    Validates that the old password entered by the user is the current password
    for the user.
    """
    def validate_password(self, user, password_change):
        if not user.check_password(password_change.old_password):
            raise StopValidation([("old_password", _("Old password is wrong"))])


class ValidateAvatarURL(UserDetailValidator):
    """
    Validates that the target avatar url currently meets constraints like
    height and width.

    .. warning::

        This validator only checks the **current** state of the image however
        if the image at the URL changes then this isn't re-run and the new
        image could break these contraints.
    """
    def validate_details(self, user, details_change):
        if not details_change.avatar:
            return

        try:
            error, ignored = check_image(details_change.avatar)
            if error:
                raise ValidationError("avatar", error)
        except RequestException:
            raise ValidationError("avatar", _("Could not retrieve avatar"))
