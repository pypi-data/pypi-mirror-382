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

""" Authentication forms """

import formencode
from formencode import validators


# auth.sign-in
class SignInForm(formencode.Schema):
    """
    :param username: The username to authenticate
    :param password: The password to validate
    :param redirect: URL to redirect to if authentication is successful
    """

    allow_extra_fields = True
    filter_extra_fields = True

    username = validators.String(not_empty=True)
    password = validators.String(not_empty=True)
    redirect = validators.String(if_missing=None, if_empty=None)
