# -*- coding: utf-8 -*-
"""
    flaskbb.core.user.update
    ~~~~~~~~~~~~~~~~~~~~~~~~

    This modules provides services used in updating user details
    across FlaskBB.

    :copyright: (c) 2014-2018 by the FlaskBB Team.
    :license: BSD, see LICENSE for more details.
"""

from abc import abstractmethod

import attr

from ..._compat import ABC


def _should_assign(current, new):
    return new is not None and current != new


@attr.s(hash=True, cmp=True, repr=True, frozen=True)
class UserDetailsChange(object):
    """
    Object representing a change user details.
    """

    birthday = attr.ib(default=None)
    gender = attr.ib(default=None)
    location = attr.ib(default=None)
    website = attr.ib(default=None)
    avatar = attr.ib(default=None)
    signature = attr.ib(default=None)
    notes = attr.ib(default=None)

    def assign_to_user(self, user):
        for (name, value) in attr.asdict(self).items():
            if _should_assign(getattr(user, name), value):
                setattr(user, name, value)


@attr.s(hash=True, cmp=True, repr=False, frozen=True)
class PasswordUpdate(object):
    """
    Object representing an update to a user's password.
    """

    old_password = attr.ib()
    new_password = attr.ib()


@attr.s(hash=True, cmp=True, repr=True, frozen=True)
class EmailUpdate(object):
    """
    Object representing a change to a user's email address.
    """

    # TODO(anr): Change to str.lower once Python2 is dropped
    old_email = attr.ib(converter=lambda x: x.lower())
    new_email = attr.ib(converter=lambda x: x.lower())


@attr.s(hash=True, cmp=True, repr=True, frozen=True)
class SettingsUpdate(object):
    """
    Object representing an update to a user's settings.
    """

    language = attr.ib()
    theme = attr.ib()

    def assign_to_user(self, user):
        for (name, value) in attr.asdict(self).items():
            if _should_assign(getattr(user, name), value):
                setattr(user, name, value)


class UserDetailsUpdateHandler(ABC):
    """
    Used to update a user's details such as birthday, location, etc.
    """

    @abstractmethod
    def update_details(self, user, details):
        """
        Recieves the current user and the
        :class:`~flaskbb.core.user.update.UserDetailsChange` containing new
        details and should update and save the current user based on this
        information. May raise a
        :class:`~flaskbb.core.exceptions.StopValidation` with the reasons that
        the change should be rejected.
        """
        pass


class UserDetailValidator(ABC):
    """
    Can be used to enforce details requirements during password changes.
    """

    @abstractmethod
    def validate_details(self, user, details_change):
        """
        May raise a :class:`~flaskbb.core.exceptions.ValidationError`
        to signify that the details doesn't meet requirements or a
        :class:`~flaskbb.core.exceptions.StopValidation` to immediately
        halt all validation.
        """
        pass


class UserDetailsUpdatePostProcessor(ABC):
    """
    Used to react to a user changing their details. This post processor
    recieves the user and the details change set that was applied to the user.
    This post processor is called after the detail changes have been persisted
    so they cannot modify the user's details without persisting again.
    """

    @abstractmethod
    def post_process_details_update(self, user, details_update):
        """
        This method is abstract.
        """
        pass


class UserPasswordUpdateHandler(ABC):
    """
    Used to validate and update a user's password.
    """

    @abstractmethod
    def update_password(self, user, password_change):
        """
        Recieves the current user and the
        :class:`~flaskbb.core.user.update.PasswordUpdate` object containing
        the information to update the user's password. May raise a
        :class:`~flaskbb.core.exceptions.StopValidation` with the reasons that
        the update should be rejected.
        """
        pass


class PasswordValidator(ABC):
    """
    Can be used to enforce password requirements during password changes.
    """

    @abstractmethod
    def validate_password(self, user, password_change):
        """
        May raise a :class:`~flaskbb.core.exceptions.ValidationError`
        to signify that the password doesn't meet the requirements or a
        :class:`~flaskbb.core.exceptions.StopValidation` to immediately
        halt all validation.
        """
        pass


class UserPasswordUpdatePostProcessor(ABC):
    """
    Used to react to a user changing their password. This post processor
    recieves the user that changed their password. This post processors is
    called after the change has been persisted so further changes to the user
    must be persisted separately.
    """

    @abstractmethod
    def post_process_password_update(self, user):
        """
        This method is abstract.
        """
        pass


class UserEmailUpdateHandler(ABC):
    """
    Used to validate and update a user's email address.
    """

    @abstractmethod
    def update_email(self, user, email_update):
        """
        Recieves the current user and the
        :class:`~flaskbb.core.user.update.EmailUpdate` object containing
        the information to update the user's email address. May raise a
        :class:`~flaskbb.core.exceptions.StopValidation` with the reasons that
        the update should be rejected.
        """
        pass


class EmailValidator(ABC):
    """
    Can be used to enforce email requirements during email changes.
    """

    @abstractmethod
    def validate_email(self, user, email_change):
        """
        May raise a :class:`~flaskbb.core.exceptions.ValidationError`
        to signify that the email doesn't meet the requirements or a
        :class:`~flaskbb.core.exceptions.StopValidation` to immediately
        halt all validation.
        """
        pass


class UserEmailUpdatePostProcessor(ABC):
    """
    Used to react to a user updating their email address. This post processor
    receives the user that changed their email and the email changes that were
    applied to the user. This post processor is called after the changes have
    been persisted so further changes to the user must be persisted separately.
    """

    @abstractmethod
    def post_process_email_update(self, user, email_update):
        """
        This method is abstract.
        """
        pass


class UserSettingsUpdateHandler(ABC):
    """
    Used to update a user's general settings in FlaskBB.
    """

    @abstractmethod
    def update_settings(self, user, settings_update):
        """
        Recieves the current user and the
        :class:`~flaskbb.core.user.update.SettingsUpdate` object containing
        the information to update the user's settings. May raise a
        :class:`~flaskbb.core.exceptions.StopValidation` with the reasons
        the the update should be rejected.
        """
        pass


class UserSettingsUpdatePostProcessor(ABC):
    """
    Used to react to a user updating their settings. This post processor
    recieves the user that updated their settings and the change set that was
    applied to the user. This post processor is called after the update has
    been persisted so further changes must be persisted separately.
    """

    @abstractmethod
    def post_process_settings_update(self, user, settings_update):
        """
        This method is abstract
        """
        pass
