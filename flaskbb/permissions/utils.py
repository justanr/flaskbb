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

from flaskbb._compat import Mapping

from .models import PermissionLevel


class PermissionManager(Mapping):

    def __init__(self, all_perms, user, forum=None, category=None):
        self._all_perms = all_perms
        self._user = user
        self._category = category
        self._forum = forum
        self.__combination = None

    @property
    def permissions(self):
        if self.__combination is None:
            self.__combination = self.__combine()
        return self.__combination

    def __getitem__(self, key):
        return self.permissions.get(key, False)

    def __iter__(self):
        return iter(self.permissions)

    def __contains__(self, name):
        return name in self.permissions

    def __len__(self):
        return len(self.permissions)

    def __combine(self):
        base = defaultdict(
            lambda: [PermissionLevel.Undefined],
            {p.name: [p.default] for p in self._all_perms},
        )

        def update_base(bag):
            for p in bag:
                base[p.permission.name] = p.value

        update_base(self._user.permissions_)
        update_base(chain(g.permissions_ for g in self._user.groups))

        if self._category:
            update_base(self._category.permissions_)

        if self._forum:
            update_base(self._forum.permissions_)
        end_result = {}

        for (name, values) in base.items():
            end_result[name] = bool(sorted(values)[-1])

        return ImmutableDict(end_result)
