# -*- coding: utf-8 -*-
"""
    flaskbb.forum
    ~~~~~~~~~~~~~

    Thie module contains models, forms, views and helpers relevant to
    forums.

    :copyright: (c) 2018 the FlaskBB Team.
    :license: BSD, see LICENSE for more details.
"""
import logging

# force plugins to be loaded
from . import plugins

logger = logging.getLogger(__name__)
__all__ = ("plugins",)
