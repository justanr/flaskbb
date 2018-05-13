# -*- coding: utf-8 -*-
"""
    flaskbb.permissions.manager
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Manager for dealing with permissions in FlaskBB

    :copyright: 2018, the FlaskBB Team
    :license: BSD, see LICENSE for more details
"""

from collections import defaultdict
from itertools import chain

from werkzeug.datastructures import ImmutableDict
from werkzeug.utils import cached_property

from flaskbb._compat import Mapping

from .models import PermissionLevel


class PermissionManager(Mapping):

    def __init__(self, all_perms, user, forum=None, category=None):
        self._all_perms = all_perms
        self._user = user
        self._category = category
        self._forum = forum

    @cached_property
    def permissions(self):
        return self._combine()

    def __getitem__(self, key):
        return self.permissions.get(key, False)

    def __iter__(self):
        return iter(self.permissions)

    def _contains__(self, name):
        return name in self.permissions

    def __len__(self):
        return len(self.permissions)

    def _combine(self):
        base = defaultdict(
            lambda: [PermissionLevel.Undefined],
            {p.name: [p.default] for p in self._all_perms},
        )

        def update_base(bag):
            for p in bag:
                if p.when_moderator and not self._is_moderator:
                    continue

                base[p.permission.name].append(p.value)

        update_base(self._all_user_permissions)

        if self._category:
            update_base(self._category.permissions_)

        if self._forum:
            update_base(self._forum.permissions_)

        return ImmutableDict(
            {name: sorted(values)[-1] for name, values in base.items()}
        )

    @cached_property
    def _is_moderator(self):
        # adminstrator and supermod status are just permissions
        # should this be an actual attribute on the user though -- user.level == Admin??
        # or merely a group membership thing?
        for p in self._all_user_permissions:
            if p.permission.name == 'admin' or p.permission.name == 'super_mod' and bool(p):
                return True

        cat_mods = getattr(self._category, 'moderators', [])
        forum_mods = getattr(self._forum, 'moderators', [])
        all_mods = chain(cat_mods, forum_mods)

        return any(self._user == mod for mod in all_mods)

    @cached_property
    def _all_user_permissions(self):
        user_perms = self._user.permissions_
        group_perms = chain.from_iterable(g.permissions_ for g in self._user.groups)
        # can't remain lazy as it's cached
        return list(chain(user_perms, group_perms))
