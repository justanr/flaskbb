.. _userprofiles:

User Profiles
=============

FlaskBB exposes several interfaces, hooks and validators to customize
user profile updates, as well as several implementations for these. For
details on the hooks see :ref:`hooks`



Data Transfer Objects
---------------------

.. autoclass:: flaskbb.core.user.update.UserDetailsChange

.. autoclass:: flaskbb.core.user.update.PasswordUpdate

.. autoclass:: flaskbb.core.user.update.EmailUpdate

.. autoclass:: flaskbb.core.user.update.SettingsUpdate

Interfaces
----------

Services
~~~~~~~~

.. autoclass:: flaskbb.core.user.update.UserDetailsUpdateHandler
    :members:

.. autoclass:: flaskbb.core.user.update.UserDetailsUpdatePostProcessor
    :members:

.. autoclass:: flaskbb.core.user.update.UserPasswordUpdateHandler
    :members:

.. autoclass:: flaskbb.core.user.update.UserPasswordUpdatePostProcessor
    :members:

.. autoclass:: flaskbb.core.user.update.UserEmailUpdateHandler
    :members:

.. autoclass:: flaskbb.core.user.update.UserEmailUpdatePostProcessor
    :members:

.. autoclass:: flaskbb.core.user.update.UserSettingsUpdateHandler
    :members:

.. autoclass:: flaskbb.core.user.update.UserSettingsUpdatePostProcessor
    :members:


Validators
~~~~~~~~~~

.. autoclass:: flaskbb.core.user.update.UserDetailValidator
    :members:

.. autoclass:: flaskbb.core.user.update.PasswordValidator
    :members:

.. autoclass:: flaskbb.core.user.update.EmailValidator
    :members:

Implementations
---------------

Services
~~~~~~~~

.. autoclass:: flaskbb.user.services.update.DefaultDetailsUpdateHandler

.. autoclass:: flaskbb.user.services.update.DefaultPasswordUpdateHandler

.. autoclass:: flaskbb.user.services.update.DefaultEmailUpdateHandler

.. autoclass:: flaskbb.user.services.update.DefaultSettingsUpdateHandler


Validators
~~~~~~~~~~

.. autoclass:: flaskbb.user.services.validators.CantShareEmailValidator
.. autoclass:: flaskbb.user.services.validators.OldEmailMustMatch
.. autoclass:: flaskbb.user.services.validators.EmailsMustBeDifferent
.. autoclass:: flaskbb.user.services.validators.PasswordsMustBeDifferent
.. autoclass:: flaskbb.user.services.validators.OldPasswordMustMatch
.. autoclass:: flaskbb.user.services.validators.ValidateAvatarURL
