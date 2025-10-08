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

""" Pyramid-Helpers functions for articles management """

import sqlalchemy as sa

from pyramid_helpers.models import DBSession
from pyramid_helpers.models.articles import Article


def create_or_modify(request, form, article=None):
    """ Create or modify function """

    translate = request.translate

    if form.errors:
        return None

    # Check title unicity
    select = sa.select(Article).where(Article.title == form.result['title'])
    same_article = DBSession.execute(select.limit(1)).scalar()
    if same_article and same_article != article:
        form.errors['title'] = translate('Title already used in another article')
        return None

    # Do the job
    if article is None:
        article = Article()
        DBSession.add(article)

    # Set author
    form.result['author'] = request.authenticated_user

    # Update object
    article.from_dict(form.result)

    # Flushing the session to get new id
    DBSession.flush()

    return article


def get_article(request):
    """ Extract article id from query and return corresponding database object """

    article_id = request.matchdict.get('article')
    if article_id is None:
        return None

    return DBSession.get(Article, article_id)


# pylint: disable=unused-argument
def search_articles(request, sort='id', order='asc', **criteria):
    """ Build a search query from criteria """

    select = sa.select(Article)

    # Filters
    if criteria.get('excluded_ids'):
        select = select.where(~Article.id.in_(criteria['excluded_ids']))

    if criteria.get('selected_ids'):
        select = select.where(Article.id.in_(criteria['selected_ids']))

    if criteria.get('term'):
        if criteria.get('exact') is True:
            select = select.where(Article.title == criteria['term'])
        else:
            select = select.where(
                Article.title.ilike('%{0}%'.format(criteria['term'].replace(' ', '%'))),
            )

    if criteria.get('title'):
        select = select.where(
            Article.title.ilike('%{0}%'.format(criteria['title'].replace(' ', '%'))),
        )

    if criteria.get('text'):
        select = select.where(
            Article.text.ilike('%{0}%'.format(criteria['text'].replace(' ', '%'))),
        )

    if criteria.get('status'):
        select = select.where(Article.status == criteria['status'])

    # Order
    if sort == 'creation_date':
        order_by = [Article.creation_date]
    elif sort == 'modification_date':
        order_by = [Article.modification_date]
    elif sort == 'title':
        order_by = [Article.title]
    elif sort == 'status':
        order_by = [Article.status]
    else:
        # Default
        order_by = [Article.id]

    sa_func = sa.asc if order == 'asc' else sa.desc
    select = select.order_by(*[sa_func(column) for column in order_by])

    return select
