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

""" SQLAlchemy utilities for Pyramid """

from sqlalchemy.orm import mapperlib
from sqlalchemy.schema import Table
from sqlalchemy.sql.annotation import AnnotatedAlias    # pylint: disable=no-name-in-module
from sqlalchemy.sql.util import find_tables


def get_entity(clause, name):
    """ Get entity by name from SQL clause """

    for entity in find_tables(clause, include_joins=True, include_aliases=True):
        if isinstance(entity, Table):
            for mapper in get_mappers(entity):
                if mapper.class_.__name__.lower() == name:
                    return mapper.entity_namespace

        elif isinstance(entity, AnnotatedAlias) and entity.name.lower() == name:
            return entity.entity_namespace

    return None


def get_mappers(table):
    """ Return associated declarative class(es) from table """

    mappers = {
        mapper
        for mapper_registry in mapperlib._all_registries()  # pylint: disable=protected-access
        for mapper in mapper_registry.mappers
        if table in mapper.tables
    }

    return sorted(mappers, key=lambda mapper: mapper.class_.__name__)
