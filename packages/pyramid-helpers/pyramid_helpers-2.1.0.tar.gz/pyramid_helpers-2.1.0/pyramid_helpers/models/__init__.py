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

""" Pyramid-Helpers data models """

import logging

from sqlalchemy import engine_from_config
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from zope.sqlalchemy import register


DBSession = scoped_session(sessionmaker())
register(DBSession)
Base = declarative_base()

log = logging.getLogger(__name__)


def includeme(config):
    """
    Set up standard configurator registrations. Use via:

    .. code-block:: python

    config = Configurator()
    config.include('pyramid_helpers.models')
    """

    registry = config.registry
    settings = registry.settings

    # Initialize model
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    log.info('[MODELS] Initialization complete: dialect=%s, engine=%s, url=%r', engine.dialect.name, engine.driver, engine.url)
