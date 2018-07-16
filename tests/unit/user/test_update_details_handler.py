from uuid import uuid4

import pytest
from pluggy import HookimplMarker

from flaskbb.core.exceptions import PersistenceError, StopValidation, ValidationError
from flaskbb.core.user.update import (
    UserDetailsChange,
    UserDetailsUpdatePostProcessor,
    UserDetailValidator,
)
from flaskbb.user.models import User
from flaskbb.user.services.update import DefaultDetailsUpdateHandler


class TestDefaultDetailsUpdateHandler(object):
    def test_raises_stop_validation_if_errors_occur(
        self, mock, user, database, plugin_manager
    ):
        validator = mock.Mock(spec=UserDetailValidator)
        validator.validate_details.side_effect = ValidationError(
            "location", "Dont be from there"
        )

        details = UserDetailsChange()
        hook_impl = mock.Mock(spec=UserDetailsUpdatePostProcessor)
        plugin_manager.register(self.impl(hook_impl))
        handler = DefaultDetailsUpdateHandler(
            validators=[validator], db=database, plugin_manager=plugin_manager
        )

        with pytest.raises(StopValidation) as excinfo:
            handler.update_details(user, details)

        assert excinfo.value.reasons == [("location", "Dont be from there")]
        hook_impl.post_process_details_update.assert_not_called()

    def test_raises_persistence_error_if_save_fails(self, mock, user, plugin_manager):
        details = UserDetailsChange()
        db = mock.Mock()
        db.session.commit.side_effect = Exception("no")

        hook_impl = mock.Mock(spec=UserDetailsUpdatePostProcessor)
        plugin_manager.register(self.impl(hook_impl))
        handler = DefaultDetailsUpdateHandler(
            validators=[], db=db, plugin_manager=plugin_manager
        )

        with pytest.raises(PersistenceError) as excinfo:
            handler.update_details(user, details)

        assert "Could not update details" in str(excinfo.value)
        hook_impl.post_process_details_update.assert_not_called()

    def test_actually_updates_users_details(self, user, database, plugin_manager, mock):
        location = str(uuid4())
        details = UserDetailsChange(location=location)
        hook_impl = mock.Mock(spec=UserDetailsUpdatePostProcessor)
        plugin_manager.register(self.impl(hook_impl))
        handler = DefaultDetailsUpdateHandler(
            db=database, plugin_manager=plugin_manager
        )

        handler.update_details(user, details)
        same_user = User.query.get(user.id)

        assert same_user.location == location
        hook_impl.post_process_details_update.assert_called_once_with(
            user=user, details_update=details
        )

    @staticmethod
    def impl(post_processor):
        class Impl:
            @HookimplMarker("flaskbb")
            def flaskbb_details_updated(self, user, details_update):
                post_processor.post_process_details_update(
                    user=user, details_update=details_update
                )

        return Impl()
