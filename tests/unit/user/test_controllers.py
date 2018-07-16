from datetime import date

import pytest
from flask import get_flashed_messages, url_for
from flask_login import current_user, login_user
from werkzeug.datastructures import MultiDict

from flaskbb.core.exceptions import PersistenceError, StopValidation
from flaskbb.core.user.update import (
    EmailUpdate,
    PasswordUpdate,
    SettingsUpdate,
    UserDetailsChange,
    UserDetailsUpdateHandler,
    UserEmailUpdateHandler,
    UserPasswordUpdateHandler,
    UserSettingsUpdateHandler,
)
from flaskbb.user.forms import (
    ChangeEmailForm,
    ChangePasswordForm,
    ChangeUserDetailsForm,
    GeneralSettingsForm,
)
from flaskbb.user.views import (
    ChangeEmail,
    ChangePassword,
    ChangeUserDetails,
    UserSettings,
)


@pytest.fixture(scope="function", autouse=True)
def setup_request(user, default_settings, post_request_context):
    login_user(user)


class TestUserSettingsView(object):
    def test_renders_get_okay(self, mock):
        form = self.produce_form({})
        handler = mock.Mock(spec=UserSettingsUpdateHandler)
        handler = UserSettings(form=form, settings_update_handler=handler)

        handler.get()

    def test_update_user_settings_successfully(self, user, mock):
        form = self.produce_form(data={"language": "python", "theme": "solarized"})
        handler = mock.Mock(spec=UserSettingsUpdateHandler)
        view = UserSettings(form=form, settings_update_handler=handler)

        result = view.post()
        flashed = get_flashed_messages(with_categories=True)

        assert len(flashed) == 1
        assert flashed[0] == ("success", "Settings updated.")
        assert result.status_code == 302
        assert result.headers["Location"] == url_for("user.settings")
        handler.update_settings.assert_called_once_with(
            user, SettingsUpdate(language="python", theme="solarized")
        )

    def test_update_user_settings_fail_with_not_valid(self, mock):
        form = self.produce_form(data={"language": "ruby", "theme": "solarized"})
        handler = mock.Mock(spec=UserSettingsUpdateHandler)
        view = UserSettings(form=form, settings_update_handler=handler)

        view.post()
        flashed = get_flashed_messages()

        assert not len(flashed)
        handler.update_settings.assert_not_called()
        assert form.errors

    def test_update_user_settings_fail_with_stopvalidation_error(self, mock):
        form = self.produce_form(data={"language": "python", "theme": "molokai"})
        handler = mock.Mock(spec=UserSettingsUpdateHandler)
        handler.update_settings.side_effect = StopValidation(
            [("theme", "Solarized is better")]
        )
        view = UserSettings(form=form, settings_update_handler=handler)

        view.post()
        flashed = get_flashed_messages()

        assert not (len(flashed))
        assert form.errors["theme"] == ["Solarized is better"]

    def test_update_user_settings_fails_with_persistence_error(self, mock):
        form = self.produce_form(data={"language": "python", "theme": "molokai"})
        handler = mock.Mock(spec=UserSettingsUpdateHandler)
        handler.update_settings.side_effect = PersistenceError("Nope")
        view = UserSettings(form=form, settings_update_handler=handler)

        result = view.post()
        flashed = get_flashed_messages(with_categories=True)

        assert len(flashed) == 1
        assert flashed[0] == ("danger", "Error while updating user settings")
        assert result.status_code == 302
        assert result.headers["Location"] == url_for("user.settings")

    def produce_form(self, data):
        form = GeneralSettingsForm(formdata=MultiDict(data), meta={"csrf": False})
        form.language.choices = [("python", "python"), ("ecmascript", "ecmascript")]
        form.theme.choices = [("molokai", "molokai"), ("solarized", "solarized")]
        return form


class TestChangePasswordView(object):
    def test_renders_get_okay(self, mock):
        form = self.produce_form()
        handler = mock.Mock(spec=UserPasswordUpdateHandler)
        view = ChangePassword(form=form, password_update_handler=handler)

        view.get()

    def test_updates_user_password_okay(self, user, mock):
        form = self.produce_form(
            old_password="password",
            new_password="newpassword",
            confirm_new_password="newpassword",
        )
        handler = mock.Mock(spec=UserPasswordUpdateHandler)
        view = ChangePassword(form=form, password_update_handler=handler)

        result = view.post()
        flashed = get_flashed_messages(with_categories=True)

        assert len(flashed) == 1
        assert flashed[0] == ("success", "Password updated.")
        assert result.status_code == 302
        assert result.headers["Location"] == url_for("user.change_password")
        handler.update_password.assert_called_once_with(
            user, PasswordUpdate(old_password="password", new_password="newpassword")
        )

    def test_updates_user_password_fails_with_invalid_inpit(self, mock, user):
        form = self.produce_form(
            old_password="password",
            new_password="newpassword",
            confirm_new_password="whoops",
        )
        handler = mock.Mock(spec=UserPasswordUpdateHandler)
        view = ChangePassword(form=form, password_update_handler=handler)

        view.post()

        handler.update_password.assert_not_called()
        assert "new_password" in form.errors

    def test_update_user_password_fails_with_stopvalidation_error(self, mock):
        form = self.produce_form(
            old_password="password",
            new_password="newpassword",
            confirm_new_password="newpassword",
        )
        handler = mock.Mock(spec=UserPasswordUpdateHandler)
        handler.update_password.side_effect = StopValidation(
            [("new_password", "That's not a very strong password")]
        )
        view = ChangePassword(form=form, password_update_handler=handler)

        view.post()

        assert form.errors["new_password"] == ["That's not a very strong password"]

    def test_update_user_password_fails_with_persistence_error(self, mock):
        form = self.produce_form(
            old_password="password",
            new_password="newpassword",
            confirm_new_password="newpassword",
        )
        handler = mock.Mock(spec=UserPasswordUpdateHandler)
        handler.update_password.side_effect = PersistenceError("no")
        view = ChangePassword(form=form, password_update_handler=handler)

        result = view.post()
        flashed = get_flashed_messages(with_categories=True)

        assert flashed == [("danger", "Error while changing password")]
        assert result.status_code == 302
        assert result.headers["Location"] == url_for("user.change_password")

    def produce_form(self, **kwargs):
        return ChangePasswordForm(
            formdata=MultiDict(kwargs), meta={"csrf": False}, obj=current_user
        )


class TestChangeEmailView(object):
    def test_renders_get_okay(self, mock):
        form = self.produce_form()
        handler = mock.Mock(spec=UserEmailUpdateHandler)
        view = ChangeEmail(form=form, update_email_handler=handler)

        view.get()

    def test_update_user_email_successfully(self, user, mock):
        form = self.produce_form(
            old_email=user.email,
            new_email="new@email.mail",
            confirm_new_email="new@email.mail",
        )
        handler = mock.Mock(spec=UserEmailUpdateHandler)
        view = ChangeEmail(form=form, update_email_handler=handler)

        result = view.post()
        flashed = get_flashed_messages(with_categories=True)

        assert flashed == [("success", "Email address updated.")]
        handler.update_email.assert_called_once_with(
            user, EmailUpdate(old_email=user.email, new_email="new@email.mail")
        )
        assert result.status_code == 302
        assert result.headers["Location"] == url_for("user.change_email")

    def test_update_user_email_fails_with_invalid_input(self, user, mock):
        form = self.produce_form(old_email=user.email, new_email="new@e.mail")
        handler = mock.Mock(spec=UserEmailUpdateHandler)
        view = ChangeEmail(form=form, update_email_handler=handler)

        view.post()

        assert form.errors
        handler.update_email.assert_not_called()

    def test_update_user_email_fails_with_stopvalidation(self, user, mock):
        form = self.produce_form(
            old_email=user.email, new_email="new@e.mail", confirm_new_email="new@e.mail"
        )
        handler = mock.Mock(spec=UserEmailUpdateHandler)
        handler.update_email.side_effect = StopValidation([("new_email", "bad email")])
        view = ChangeEmail(form=form, update_email_handler=handler)

        view.post()

        assert form.errors == {"new_email": ["bad email"]}

    def test_update_email_fails_with_persistence_error(self, user, mock):
        form = self.produce_form(
            old_email=user.email, new_email="new@e.mail", confirm_new_email="new@e.mail"
        )
        handler = mock.Mock(spec=UserEmailUpdateHandler)
        handler.update_email.side_effect = PersistenceError("nope")
        view = ChangeEmail(form=form, update_email_handler=handler)

        result = view.post()
        flashed = get_flashed_messages(with_categories=True)

        assert flashed == [("danger", "Error while updating email")]
        assert result.status_code == 302
        assert result.headers["Location"] == url_for("user.change_email")

    def produce_form(self, **data):
        return ChangeEmailForm(
            formdata=MultiDict(data),
            user=current_user,
            meta={"csrf": False},
        )


class TestChangeUserDetailsView(object):
    def test_renders_get_okay(self, mock):
        form = self.produce_form()
        handler = mock.Mock(spec=UserSettingsUpdateHandler)
        view = ChangeUserDetails(form=form, details_update_handler=handler)

        view.get()

    def test_update_user_details_successfully_updates(self, user, mock):
        form = self.produce_form(
            birthday="25 04 2000",
            gender="awesome",
            location="here",
            website="http://web.site",
            avatar="http://web.site/avatar.png",
            signature="use a cursive font",
            notes="got 'em",
        )
        handler = mock.Mock(spec=UserDetailsUpdateHandler)
        view = ChangeUserDetails(form=form, details_update_handler=handler)

        result = view.post()
        flashed = get_flashed_messages(with_categories=True)

        assert flashed == [("success", "User details updated.")]
        assert result.status_code == 302
        assert result.headers["Location"] == url_for("user.change_user_details")
        handler.update_details.assert_called_once_with(
            user,
            UserDetailsChange(
                birthday=date(2000, 4, 25),
                gender="awesome",
                location="here",
                website="http://web.site",
                avatar="http://web.site/avatar.png",
                signature="use a cursive font",
                notes="got 'em",
            ),
        )

    def test_update_user_fails_with_invalid_input(self, mock):
        form = self.produce_form(birthday="99 99 999999")
        handler = mock.Mock(spec=UserEmailUpdateHandler)
        view = ChangeUserDetails(form=form, details_update_handler=handler)

        view.post()

        assert form.errors == {"birthday": ["Not a valid date value"]}

    def test_update_user_fails_with_stopvalidation(self, mock):
        form = self.produce_form(birthday="25 04 2000")
        handler = mock.Mock(spec=UserDetailsUpdateHandler)
        handler.update_details.side_effect = StopValidation(
            [("birthday", "I just want you to know that's a great birthday")]
        )
        view = ChangeUserDetails(form=form, details_update_handler=handler)

        view.post()

        assert form.errors == {
            "birthday": ["I just want you to know that's a great birthday"]
        }

    def test_update_user_fails_with_persistence_error(self, mock):
        form = self.produce_form(birthday="25 04 2000")
        handler = mock.Mock(spec=UserDetailsUpdateHandler)
        handler.update_details.side_effect = PersistenceError("no")
        view = ChangeUserDetails(form=form, details_update_handler=handler)

        result = view.post()
        flashed = get_flashed_messages(with_categories=True)

        assert flashed == [("danger", "Error while updating user details")]
        assert result.status_code == 302
        assert result.headers["Location"] == url_for("user.change_user_details")

    def produce_form(self, **kwargs):
        return ChangeUserDetailsForm(
            obj=current_user, formdata=MultiDict(kwargs), meta={"csrf": False}
        )
