from itertools import chain

from flask_allows import Permission
from flask_babelplus import gettext as _
from pluggy import HookimplMarker

from ..display.navigation import NavigationDivider, NavigationLink
from ..utils.requirements import IsAtleastModerator
from ..utils.settings import flaskbb_config

impl = HookimplMarker("flaskbb")


def _get_logged_in_nav(user):
    results = [
        NavigationLink(
            endpoint="forum.topictracker",
            name=_("Topic Tracker"),
            icon="fa fa-book fa-fw",
            urlforkwargs={"username": user.username},
        ),
        NavigationDivider(),
        NavigationLink(
            endpoint="user.settings", name=_("Settings"), icon="fa fa-cogs fa-fw"
        ),
    ]

    if Permission(IsAtleastModerator, identity=user):
        results.extend(
            [
                NavigationLink(
                    endpoint="management.overview",
                    name=_("Management"),
                    icon="fa fa-cog fa-fw",
                )
            ]
        )

    results.extend(
        [
            NavigationDivider(),
            NavigationLink(
                endpoint="auth.logout", name=_("Logout"), icon="fa fa-power-off fa-fw"
            ),
        ]
    )
    return results


def _get_logged_out_nav():
    results = []
    if flaskbb_config["REGISTRATION_ENABLED"]:
        results.append(
            NavigationLink(
                endpoint="auth.register",
                name=_("Register"),
                icon="fa fa-user-plus fa-fw",
            )
        )

    results.append(
        NavigationLink(
            endpoint="auth.forgot_password",
            name=_("Reset Password"),
            icon="fa fa-undo fa-fw",
        )
    )

    if flaskbb_config["ACTIVATE_ACCOUNT"]:
        results.append(
            NavigationLink(
                endpoint="auth.request_activation_token",
                name=_("Activate Account"),
                icon="fa fa-fw fa-ticket",
            )
        )

    return results


@impl(hookwrapper=True, tryfirst=True)
def flaskbb_tpl_user_nav_menu(user):
    if user.is_authenticated:
        results = _get_logged_in_nav(user)
    else:
        results = _get_logged_out_nav()

    outcome = yield
    outcome.force_result(chain(results, *outcome.get_result()))
