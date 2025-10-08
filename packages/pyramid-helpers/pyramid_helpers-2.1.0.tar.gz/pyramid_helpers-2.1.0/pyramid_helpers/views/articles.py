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

""" Pyramid-Helpers views for articles management """

from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

import sqlalchemy as sa

from pyramid_helpers.forms import validate
from pyramid_helpers.forms.articles import CreateForm
from pyramid_helpers.funcs.articles import create_or_modify
from pyramid_helpers.funcs.articles import get_article
from pyramid_helpers.funcs.articles import search_articles
from pyramid_helpers.models import DBSession
from pyramid_helpers.models.articles import Article
from pyramid_helpers.paginate import paginate


@view_config(permission='articles.create', route_name='articles.create', renderer='/articles/modify.mako')
@validate('article', CreateForm)
def create(request):
    """ Creates an article """

    translate = request.translate
    form = request.forms['article']

    if request.method == 'POST':
        article = create_or_modify(request, form)
        if article:
            return HTTPFound(location=request.route_path('articles.visual', article=article.id))

    breadcrumb = [
        (translate('Articles'), request.route_path('articles.search')),
        (translate('New article'), request.route_path('articles.create'))
    ]
    title = translate('New article')
    cancel_link = request.route_path('articles.search')

    return {
        'breadcrumb': breadcrumb,
        'cancel_link': cancel_link,
        'title': title,
    }


@view_config(permission='articles.delete', route_name='articles.delete', renderer='/confirm.mako')
def delete(request):
    """ Deletes an article """

    translate = request.translate

    article = get_article(request)
    if article is None:
        raise HTTPNotFound(detail=translate('Invalid article'))

    if request.method == 'POST':
        if 'cancel' in request.params:
            return HTTPFound(location=request.route_url('articles.visual', article=article.id))

        DBSession.delete(article)
        return HTTPFound(location=request.route_url('articles.search'))

    breadcrumb = [
        (translate('Articles'), request.route_path('articles.search')),
        (article.title, request.route_path('articles.visual', article=article.id)),
        (translate('Deletion'), request.route_path('articles.delete', article=article.id)),
    ]
    return {
        'breadcrumb': breadcrumb,
        'note': None,
        'question': translate('Do you really want to delete article "{0}" ?').format(article.title),
        'title': translate('Article "{0}" deletion').format(article.title),
    }


@view_config(permission='articles.modify', route_name='articles.modify', renderer='/articles/modify.mako')
@validate('article', CreateForm)
def modify(request):
    """ Modifies an article """

    translate = request.translate
    form = request.forms['article']

    article = get_article(request)
    if article is None:
        raise HTTPNotFound(detail=translate('Invalid article'))

    if request.method == 'POST':
        if create_or_modify(request, form, article=article):
            return HTTPFound(location=request.route_url('articles.visual', article=article.id))
    else:
        data = article.to_dict()
        form.from_python(data)

    breadcrumb = [
        (translate('Articles'), request.route_path('articles.search')),
        (article.title, request.route_path('articles.visual', article=article.id)),
        (translate('Edition'), request.route_path('articles.modify', article=article.id)),
    ]
    title = translate('Article "{0}" edition').format(article.title)
    cancel_link = request.route_url('articles.visual', article=article.id)

    return {
        'breadcrumb': breadcrumb,
        'cancel_link': cancel_link,
        'title': title,
    }


@view_config(permission='articles.visual', route_name='articles.search', renderer='/articles/search.mako')
@paginate('articles', limit=10, sort='id', order='desc', partial_template='/articles/list.mako')
def search(request):
    """ Search for articles """

    translate = request.translate
    pager = request.pagers['articles']

    if not request.has_permission('articles.modify'):
        criteria = {'status': 'published'}
    else:
        criteria = {}

    select = search_articles(request, order=pager.order, sort=pager.sort, **criteria)

    def get_items(offset, limit):
        return DBSession.execute(select.offset(offset).limit(limit)).scalars().all()

    # pylint: disable=not-callable
    count = DBSession.execute(select.with_only_columns(sa.func.count(Article.id)).order_by(None)).scalar()
    pager.set_collection(count=count, items=get_items)

    if pager.partial:
        return {}

    if 'csv' in request.params:
        # CSV export
        request.override_renderer = 'csv'

        rows = []

        # Add header
        rows.append([
            translate('id'),
            translate('title'),
            translate('creation date'),
            translate('status'),
            translate('text'),
        ])

        # Add content
        rows.extend([
            [article.id, article.title, article.creation_date, article.status, article.text]
            for article in DBSession.execute(select).scalars()
        ])

        return {
            'delimiter': ';',
            'filename': translate('articles.csv'),
            'rows': rows,
        }

    breadcrumb = [
        (translate('Articles'), request.route_path('articles.search'))
    ]

    return {
        'breadcrumb': breadcrumb,
        'title': translate('Articles')
    }


@view_config(permission='articles.visual', route_name='articles.visual', renderer='/articles/visual.mako')
def visual(request):
    """ Visualizes an article """

    translate = request.translate

    article = get_article(request)
    if article is None:
        raise HTTPNotFound(detail=translate('Invalid article'))

    breadcrumb = [
        (translate('Articles'), request.route_path('articles.search')),
        (article.title, request.route_path('articles.visual', article=article.id)),
    ]
    return {
        'article': article,
        'breadcrumb': breadcrumb,
        'title': article.title
    }
