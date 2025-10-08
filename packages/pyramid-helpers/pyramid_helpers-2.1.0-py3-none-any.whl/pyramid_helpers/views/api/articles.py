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

"""
Articles API
"""

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

import sqlalchemy as sa

from pyramid_helpers.forms import validate
from pyramid_helpers.forms.articles import CreateForm
from pyramid_helpers.forms.articles import SearchForm
from pyramid_helpers.forms.articles import StatusForm
from pyramid_helpers.funcs.articles import create_or_modify
from pyramid_helpers.funcs.articles import get_article
from pyramid_helpers.funcs.articles import search_articles
from pyramid_helpers.models import DBSession
from pyramid_helpers.models.articles import Article
from pyramid_helpers.paginate import paginate


@view_config(route_name='api.articles.create', renderer='json', permission='articles.create')
@validate('article', CreateForm)
def create(request):
    """
    Creates an article
    """
    form = request.forms['article']

    article = create_or_modify(request, form)
    if article is None:
        raise HTTPBadRequest(json=form.errors)

    result = {
        'url': request.path_qs,
        'method': request.method,
        'params': form.params,
        'apiVersion': '1.0',
        'result': True,
        'article': article.to_dict(context='create'),
    }

    request.response.status_int = 201
    return result


@view_config(route_name='api.articles.delete', renderer='json', permission='articles.delete')
def delete(request):
    """
    Deletes an article
    """
    translate = request.translate

    article = get_article(request)
    if article is None:
        raise HTTPNotFound(detail=translate('Invalid article'))

    DBSession.delete(article)

    result = {
        'url': request.path_qs,
        'method': request.method,
        'apiVersion': '1.0',
        'result': True,
    }

    return result


@view_config(route_name='api.articles.modify', renderer='json', permission='articles.modify')
@validate('article', CreateForm)
def modify(request):
    """
    Modifies an article
    """
    translate = request.translate
    form = request.forms['article']

    article = get_article(request)
    if article is None:
        raise HTTPNotFound(detail=translate('Invalid article'))

    if not create_or_modify(request, form, article=article):
        raise HTTPBadRequest(json=form.errors)

    result = {
        'url': request.path_qs,
        'method': request.method,
        'params': form.params,
        'apiVersion': '1.0',
        'result': True,
        'article': article.to_dict(context='modify'),
    }

    return result


@view_config(route_name='api.articles.status', renderer='json', permission='articles.modify')
@validate('status', StatusForm)
def status(request):
    """
    Changes an article status
    """
    translate = request.translate
    form = request.forms['status']

    article = get_article(request)
    if article is None:
        raise HTTPNotFound(detail=translate('Invalid article'))

    if form.errors:
        raise HTTPBadRequest(json=form.errors)

    # Update object
    article.from_dict(form.result)

    result = {
        'url': request.path_qs,
        'method': request.method,
        'params': form.params,
        'apiVersion': '1.0',
        'result': True,
        'article': article.to_dict(context='modify'),
    }

    return result


@view_config(route_name='api.articles.search', renderer='json', permission='articles.search')
@paginate('articles', limit=10, sort='id', order='desc')
@validate('search', SearchForm, method='get')
def search(request):
    """
    Searches in articles
    """
    form = request.forms['search']
    pager = request.pagers['articles']

    if form.errors:
        raise HTTPBadRequest(json=form.errors)

    select = search_articles(request, order=pager.order, sort=pager.sort, **form.result)

    def get_items(offset, limit):
        return DBSession.execute(select.offset(offset).limit(limit)).scalars().all()

    # pylint: disable=not-callable
    count = DBSession.execute(select.with_only_columns(sa.func.count(Article.id)).order_by(None)).scalar()
    pager.set_collection(count=count, items=get_items)

    result = {
        'url': request.path_qs,
        'method': request.method,
        'params': form.params,
        'apiVersion': '1.0',
        'result': True,
        'articles': {
            'items': [article.to_dict(context='search') for article in pager],
            'pager': pager.to_dict(),
        }
    }

    return result


@view_config(route_name='api.articles.visual', renderer='json', permission='articles.visual')
def visual(request):
    """
    Gets an article
    """
    translate = request.translate

    article = get_article(request)
    if article is None:
        raise HTTPNotFound(detail=translate('Invalid article'))

    result = {
        'url': request.path_qs,
        'method': request.method,
        'apiVersion': '1.0',
        'result': True,
        'article': article.to_dict(context='visual'),
    }

    return result
