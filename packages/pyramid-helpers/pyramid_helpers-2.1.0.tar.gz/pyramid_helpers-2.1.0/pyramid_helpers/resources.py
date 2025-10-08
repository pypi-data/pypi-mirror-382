# pyramid-helpers -- Helpers to develop Pyramid applications
# By: Cyril Lacoux <clacoux@easter-eggs.com>
#     Valéry Febvre <vfebvre@easter-eggs.com>
#
# https://gitlab.com/yack/pyramid-helpers
#
# SPDX-FileCopyrightText: © Cyril Lacoux <clacoux@easter-eggs.com>
# SPDX-FileCopyrightText: © Easter-eggs <https://easter-eggs.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

""" Pyramid-Helpers resources """

from pyramid.authorization import ALL_PERMISSIONS
from pyramid.authorization import Allow
from pyramid.authorization import Everyone


class Root:
    """ Pyramid-Helpers resources """

    __acl__ = [
        (Allow, Everyone, (
            'articles.search',
            'articles.visual',
        )),

        (Allow, 'group:admin', ALL_PERMISSIONS),

        (Allow, 'group:guest', (
            'articles.create',
            'articles.modify',
        )),
    ]

    def __init__(self, request):
        self.request = request
