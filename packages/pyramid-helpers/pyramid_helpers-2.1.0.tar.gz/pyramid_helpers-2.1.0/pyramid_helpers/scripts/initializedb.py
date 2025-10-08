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

""" Database initialization script """

from argparse import ArgumentParser
import sys
import transaction

from pyramid.config import Configurator
from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging

import sqlalchemy as sa

from pyramid_helpers.models import Base
from pyramid_helpers.models import DBSession
from pyramid_helpers.models.articles import Article
from pyramid_helpers.models.core import Group
from pyramid_helpers.models.core import User
from pyramid_helpers.utils import random_string


USERS = {
    'admin': {
        'groups': ['admin', ],
        'password': 'admin',
    },
    'guest': {
        'groups': ['guest', ],
        'password': 'guest',
    },
}


def add_articles():
    """ Add some articles to database for test purpose """

    author = DBSession.execute(sa.select(User).where(User.username == 'admin').limit(1)).scalar()

    def add_article(data, author=author):
        data['author'] = author

        article = Article()
        DBSession.add(article)

        article.from_dict(data)

    # For searches (1-99)
    for i in range(1, 100):
        add_article({
            'title': f'Article #{i}',
            'text': f'Text of article #{i}',
            'status': 'published',
        })

    # For modifications (100-101)
    for i in range(1, 3):
        add_article({
            'title': f'Article to modify #{i}',
            'text': f'Text of article to modify #{i}',
            'status': 'draft',
        })

    # For deletions (102-103)
    for i in range(1, 3):
        add_article({
            'title': f'Article to remove #{i}',
            'text': f'Text of article to remove #{i}',
            'status': 'draft',
        })


def add_users(users):
    """ Add some users to database for test purpose """

    def add_user(username, **data):
        groups = []
        for group_name in data.pop('groups', []):
            group = DBSession.execute(sa.select(Group).where(Group.name == group_name).limit(1)).scalar()
            if group is None:
                # Add group to database
                group = Group()
                DBSession.add(group)

                group.name = group_name

            group.from_dict({
                'description': f'{group_name} group description',
            })

            groups.append(group)

        user = DBSession.execute(sa.select(User).where(User.username == username).limit(1)).scalar()
        if user is None:
            # Add user to database
            user = User()
            DBSession.add(user)

            user.username = username

        data.update({
            'groups': groups,
            'status': 'active',
            'token': random_string(40),
        })

        user.from_dict(data)

    for username, data in users.items():
        add_user(username, **data)


def main(argv=None):
    """ Database initialization """

    if argv is None:
        argv = sys.argv[1:]

    parser = ArgumentParser(description='Database initialization script')

    parser.add_argument(
        'config_uri',
        help='Configuration file to use.'
    )

    args = parser.parse_args(argv)

    setup_logging(args.config_uri)

    try:
        # Production
        settings = get_appsettings(args.config_uri, name='pyramid-helpers')
    except LookupError:
        # Development
        settings = get_appsettings(args.config_uri)

    config = Configurator(settings=settings)

    # Model setup
    config.include('pyramid_helpers.models')

    Base.metadata.create_all(bind=DBSession.get_bind())

    # Populate table users
    with transaction.manager:
        add_users(USERS)

    # Flush table articles
    with transaction.manager:
        DBSession.execute(sa.delete(Article))

    # Populate table articles
    with transaction.manager:
        add_articles()
