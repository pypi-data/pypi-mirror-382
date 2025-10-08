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

""" Pyramid-Helpers common views """

import hashlib

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.security import forget
from pyramid.security import remember
from pyramid.view import exception_view_config
from pyramid.view import view_config

from pyramid_helpers.api_doc import api_doc as api_doc_
from pyramid_helpers.auth import check_credentials
from pyramid_helpers.forms import validate
from pyramid_helpers.forms.auth import SignInForm
from pyramid_helpers.forms.validators import ValidatorsForm
from pyramid_helpers.i18n import N_
from pyramid_helpers.utils import get_settings


# HTTPExceptions' titles
N_('Bad Request')
N_('Forbidden')
N_('Not Found')

N_('Access was denied to this resource.')
N_('The resource could not be found.')


@view_config(route_name='api-doc', renderer='')
def api_doc(request):
    """ The API doc view """

    translate = request.translate

    renderer_values = {
        'breadcrumb': [(translate('API documentation'), None)],
        'subtitle': None,
        'title': translate('API documentation'),
    }

    return api_doc_(request, renderer_values)


@exception_view_config(HTTPBadRequest, renderer='/errors.mako')
def http_400(request):
    """ HTTP 400 error view """

    translate = request.translate

    request.response.status_int = 400

    if request.matched_route.name.startswith('api.'):
        request.override_renderer = 'json'
        return {
            'url': request.path_qs,
            'method': request.method,
            'params': request.params.mixed(),
            'errors': request.exception.json if request.exception.body else {},
            'apiVersion': '1.0',
            'result': False,
            'message': request.exception.message or translate('Invalid or missing parameter(s)'),
        }

    # Prevent from rendering wrong template
    if hasattr(request, 'override_renderer'):
        del request.override_renderer

    return {
        'title': translate(request.exception.title),
        'subtitle': None,
    }


@exception_view_config(HTTPForbidden, renderer='/errors.mako')
@exception_view_config(HTTPUnauthorized, renderer='/errors.mako')
def http_403(request):
    """ HTTP 403 error view """

    translate = request.translate

    if request.authenticated_user is None:
        params = get_settings(request, 'auth', 'auth')
        if params.get('policies') == ['basic']:
            # Issuing a challenge
            response = HTTPUnauthorized()
            response.headers.update(forget(request))
            return response

        return HTTPFound(location=request.route_path('auth.sign-in', _query={'redirect': request.path_qs}))

    request.response.status_int = 403

    if request.matched_route.name.startswith('api.'):
        request.override_renderer = 'json'
        return {
            'url': request.path_qs,
            'method': request.method,
            'params': request.params.mixed(),
            'apiVersion': '1.0',
            'result': False,
            'message': request.exception.message or translate('Access denied'),
        }

    # Prevent from rendering wrong template
    if hasattr(request, 'override_renderer'):
        del request.override_renderer

    return {
        'title': translate(request.exception.title),
        'subtitle': '',
    }


@exception_view_config(HTTPNotFound, renderer='/errors.mako')
def http_404(request):
    """ HTTP 404 error view """

    translate = request.translate

    request.response.status_int = 404

    if request.matched_route and request.matched_route.name.startswith('api.'):
        request.override_renderer = 'json'
        return {
            'url': request.path_qs,
            'method': request.method,
            'params': request.params.mixed(),
            'apiVersion': '1.0',
            'result': False,
            'message': request.exception.message or translate('Not found'),
        }

    # Prevent from rendering wrong template
    if hasattr(request, 'override_renderer'):
        del request.override_renderer

    return {
        'title': translate(request.exception.title),
        'subtitle': '',
    }


@view_config(route_name='index', renderer='index.mako')
def index(request):
    """ Index view """

    translate = request.translate

    return {
        'breadcrumb': [],
        'title': 'Pyramid Helpers',
        'subtitle': translate('Home'),
    }


@view_config(route_name='i18n', renderer='/i18n.mako')
def i18n(request):
    """ I18n view """

    translate = request.translate

    return {
        'breadcrumb': [
            (translate('I18n'), None),
        ],
        'title': translate('I18n page'),
        'subtitle': '',
    }


@view_config(route_name='predicates', renderer='/predicates.mako')
@view_config(route_name='predicates.enum', renderer='/predicates.mako')
@view_config(route_name='predicates.numeric-1', renderer='/predicates.mako')
@view_config(route_name='predicates.numeric-2', renderer='/predicates.mako')
def predicates(request):
    """ Predicates view """

    translate = request.translate

    return {
        'breadcrumb': [
            (translate('Predicates'), None),
        ],
        'title': translate('Predicates page'),
        'subtitle': '',
    }


@view_config(route_name='auth.sign-in', renderer='/auth/sign-in.mako')
@validate('signin', SignInForm)
def sign_in(request):
    """ Sign-in view """

    translate = request.translate
    form = request.forms['signin']

    params = get_settings(request, 'auth', 'auth')
    if params.get('policies') == ['remote']:
        params = get_settings(request, 'auth', 'policy:remote')
        login_url = params.get('login_url')
        if login_url is None:
            raise HTTPInternalServerError(detail=translate('Authentication not available, please retry later.'))

        return HTTPFound(location=login_url)

    if request.method == 'POST':
        if not form.errors:
            username = form.result['username']
            password = form.result['password']
            redirect = form.result['redirect']

            if check_credentials(username, password, request, principals=False):
                headers = remember(request, username)
                return HTTPFound(location=redirect, headers=headers)

            form.errors['username'] = translate('Bad user or password')
    else:
        redirect = request.GET.get('redirect')
        if redirect is None or redirect == request.current_route_url(_query=None):
            redirect = request.route_path('index')

        data = {'redirect': redirect}
        form.from_python(data)

    return {
        'title': translate('Authentication'),
    }


@view_config(route_name='auth.sign-out', renderer='/auth/sign-out.mako')
def sign_out(request):
    """ Sign-out view """

    session = request.session
    translate = request.translate

    # Clear session
    session.delete()

    if request.authentication_policy == 'remote':
        params = get_settings(request, 'auth', 'policy:remote')
        logout_url = params.get('logout_url')
        if logout_url is None:
            # Display logout page
            return {
                'title': translate('Logged out'),
            }
    else:
        logout_url = request.route_path('index')

    headers = forget(request)
    return HTTPFound(location=logout_url, headers=headers)


@view_config(route_name='validators', renderer='/validators.mako')
@validate('validators_form', ValidatorsForm, extract='post')
def validators(request):
    """ Validators view """

    translate = request.translate
    form = request.forms['validators_form']

    if request.method == 'POST':
        if not form.errors:
            qfile = form.result['upload_input']
            if qfile is not None:
                content = qfile.file.read()
                form.result['upload_input.name'] = qfile.filename
                form.result['upload_input.size'] = len(content)
                form.result['upload_input.sha256'] = hashlib.sha256(content).hexdigest()

    return {
        'breadcrumb': [(translate('Validators'), None)],
        'errors': form.errors,
        'result': form.result,
    }
