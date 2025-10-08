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
Authentication module for Pyramid-Helpers

Useful documentation can be found at:
 * https://docs.pylonsproject.org/projects/pyramid/en/latest/api/security.html
 * https://docs.pylonsproject.org/projects/pyramid-cookbook/en/latest/auth/index.html
"""

import hashlib
import logging

from beaker.util import NoneType

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authentication import BasicAuthAuthenticationPolicy
from pyramid.authentication import CallbackAuthenticationPolicy
from pyramid.authentication import RemoteUserAuthenticationPolicy as RemoteUserAuthenticationPolicy_
from pyramid.authentication import extract_http_basic_credentials
from pyramid.authorization import ACLHelper

from pyramid_helpers.utils import ConfigurationError
from pyramid_helpers.utils import get_settings
from pyramid_helpers.utils import parse_settings
from pyramid_helpers.utils import request_cache
from pyramid_helpers.utils import resolve_dotted


BACKENDS = {}

SETTINGS_DEFAULTS = {
    'auth': {
        'backend': None,
        'callback': None,
        'policies': ['cookie', ],
        'get_user_by_username': None,
    },
    'policy:basic': {
        'realm': 'Pyramid-Helpers Application',
        'identify': None,
    },
    'policy:cookie': {
        'secret': 'the-big-secret-for-secured-authentication',
        'hashalg': 'sha512',
    },
    'policy:remote': {
        'fake_user': None,
        'header': None,
        'identify': None,
        'login_url': None,
        'logout_url': None,
    },
    'policy:token': {
        'header': 'X-PH-Authentication-Token',
        'scheme': None,
        'query_param': None,
        'identify': None,
    },
}

SETTINGS_RULES = {
    'auth': [
        ('enabled', (bool, NoneType), 'enabled must be a boolean or an integer'),
        ('backend', (str, NoneType), 'backend must be a string designating a valid backend'),
        ('callback', (str,), 'callback must be a string designating a valid callback'),
        ('policies', (list, NoneType), 'policies must be a comma separated list of policies'),
        ('get_user_by_username', (str,), 'get_user_by_username must be a string designating a valid callback'),
    ],
    'policy:basic': [
        ('realm', (str, NoneType), 'realm must be a string designating a realm authentication'),
        ('identify', (str, NoneType), 'identify must be a string designating a valid callback'),
    ],
    'policy:cookie': [
        ('secret', (str, NoneType), 'secret must be a string designating a secret'),
        ('hashalg', (str, NoneType), 'hashalg must be a string designating a valid hashalg'),
        ('identify', (str, NoneType), 'identify must be a string designating a valid callback'),
    ],
    'policy:remote': [
        ('fake_user', (str, NoneType), 'fake_user must be a string designating a username'),
        ('header', (str, NoneType), 'header must be a string designating a HTTP header'),
        ('login_url', (str, NoneType), 'login_url must be a string designating a valid url'),
        ('logout_url', (str, NoneType), 'logout_url must be a string designating a valid url'),
        ('identify', (str, NoneType), 'identify must be a string designating a valid callback'),
    ],
    'policy:token': [
        ('header', (str, NoneType), 'header must be a string designating a HTTP header'),
        ('scheme', (str, NoneType), 'scheme must be a string designating an authentication scheme'),
        ('query_param', (str, NoneType), 'query_param must be a string designating a query parameter'),
        ('identify', (str, NoneType), 'identify must be a string designating a valid callback'),
    ],
}


log = logging.getLogger(__name__)


#
# Authentication backends
#

class AuthenticationBackend:
    """ Authentication backend base class """

    __name__ = None

    def __enter__(self):
        """
        This method is called by the `with:` statement and should be overridden
        to execute some tasks **before** validating the password.
        """

        return self

    def __exit__(self, type_, value, traceback):
        """
        This method is called by the `with:` statement and should be overridden
        to execute some tasks **after** validating the password.
        """

    # pylint: disable=unused-argument
    def setup(self, *args, **kwargs):
        """ Register authentication backend """

        if self.__name__ is None:
            log.error('[AUTH] Attribute `.__name__` of AuthenticationBackend instance must be set')
            return False

        if self.__name__ in BACKENDS:
            log.error('[AUTH] An authentication backend is already registered for %s', self.__name__)
            return False

        # Registering object
        BACKENDS[self.__name__] = self

        log.info('[AUTH] Registered authentication backend, name=%s, class=%s', self.__name__, self.__class__.__name__)

        return True

    def validate_password(self, request, username, password):
        """ Please, override this method to implement the password validation """

        raise NotImplementedError()


class DatabaseAuthenticationBackend(AuthenticationBackend):
    """ Authentication backend for database """

    __name__ = 'database'

    def validate_password(self, request, username, password):
        """ Validate password """

        user = get_user_by_username(request, username)
        if user is None:
            return False

        return user.validate_password(password)


#
# Authentication policies
#

class CachedEffectivePrincipals:
    """ Mixin that caches the effective principals """

    @request_cache()
    def effective_principals(self, request):
        """ Get the list of effective principals """

        # pylint: disable=no-member
        # Calling inherited
        return super().effective_principals(request)


class BasicAuthenticationPolicy(CachedEffectivePrincipals, BasicAuthAuthenticationPolicy):
    """ Authentication policy for HTTP/Basic authentication """

    def __init__(self, check, identify=None, realm='Pyramid-Helpers'):

        # Calling inherited
        super().__init__(check, realm=realm)

        self._identify = identify

    def identify(self, request):
        """ Identify the user """

        credentials = extract_http_basic_credentials(request)
        if credentials is None:
            return None

        if not check_credentials(credentials.username, credentials.password, request, principals=False):
            return None

        return self._identify(request, credentials.username)

    def is_available(self, request):
        """ Check if authentication credentials are in request """

        return extract_http_basic_credentials(request) is not None


class CookieAuthenticationPolicy(CachedEffectivePrincipals, AuthTktAuthenticationPolicy):
    """ Authentication policy for cookie based authentication """

    def identify(self, request):
        """ Identify the user """

        return self.cookie.identify(request)

    def is_available(self, request):
        """ Check if cookie is present in request """

        return request.cookies.get(self.cookie.cookie_name) is not None


class TokenAuthenticationPolicy(CachedEffectivePrincipals, CallbackAuthenticationPolicy):
    """ Authentication policy for token authentication """

    def __init__(self, callback=None, identify=None):

        self.callback = callback
        self._identify = identify

    def forget(self, request):              # pylint: disable=unused-argument
        """ Forget authentication """

        return []

    def identify(self, request):
        """ Identify the user """

        token = extract_token(request)
        if token is None:
            return None

        return self._identify(request, token)

    def is_available(self, request):
        """ Check if authentication token is in request """

        return extract_token(request) is not None

    def remember(self, request, userid):    # pylint: disable=unused-argument
        """ Remember authentication """

        return []

    def unauthenticated_userid(self, request):
        """ The userid associated with token """

        identity = self.identify(request)
        if identity is None:
            return None

        return identity['userid']


class RemoteUserAuthenticationPolicy(CachedEffectivePrincipals, RemoteUserAuthenticationPolicy_):
    """ Authentication policy for remote authentication """

    def __init__(self, environ_key='REMOTE_USER', callback=None, identify=None):

        # Calling inherited
        super().__init__(environ_key=environ_key, callback=callback)

        self._identify = identify

    def identify(self, request):
        """ Identify the user """

        userid = self.unauthenticated_userid(request)
        if userid is None:
            return None

        return self._identify(request, userid)

    def is_available(self, request):
        """ Check if remote user is present in request """

        return request.environ.get(self.environ_key) is not None


#
# Security policy
#

class MultiSecurityPolicy:
    """ A Pyramid security policy that implements multiple security policies """

    POLICIES = ['cookie', 'basic', 'token', 'remote']     # Order matters

    def __init__(self, policies):

        self.policies = policies

    @request_cache()
    def authenticated_userid(self, request):
        """ Get user id identifying the trusted and verified user, or None if unauthenticated """

        identity = request.identity
        if identity is None:
            return None

        return identity['userid']

    def forget(self, request):
        """ Get set of headers suitable for «forgetting» the current user on subsequent requests """

        policy = self.get_policy(request)
        return policy.forget(request)

    @request_cache()
    def get_policy(self, request):
        """ Get authentication policy from request """

        if hasattr(request, 'authentication_policy'):
            log.debug('[AUTH] Using set policy: %s', request.authentication_policy)
            return self.policies[request.authentication_policy]

        policy = request.headers.get('X-PH-Authentication-Policy')

        log.debug('[AUTH] Requested policy: %s', policy)

        if policy is None:
            # Guess available policy from request
            for policy_ in self.POLICIES:
                if policy_ in self.policies and self.policies[policy_].is_available(request):
                    policy = policy_
                    log.debug('[AUTH] Using detected policy: %s', policy)
                    break

        if policy not in self.policies:
            # Get first usable policy
            for policy_ in self.POLICIES:
                if policy_ in self.policies:
                    policy = policy_
                    log.debug('[AUTH] Using default policy: %s', policy)
                    break

        # Store policy to request
        request.authentication_policy = policy

        return self.policies[policy]

    @request_cache()
    def identity(self, request):
        """ Get the identity of the current user """

        policy = self.get_policy(request)

        identity = policy.identify(request)
        if identity is None:
            return None

        return identity

    def permits(self, request, context, permission):
        """
        Get an instance of `pyramid.security.Allowed` if a user of the given identity is allowed the permission in the current context,
        else return an instance of `pyramid.security.Denied`
        """

        policy = self.get_policy(request)
        return ACLHelper().permits(context, policy.effective_principals(request), permission)

    def remember(self, request, username, **kw):
        """ Get set of headers suitable for «remembering« the user id """

        policy = self.get_policy(request)
        return policy.remember(request, username, **kw)

    @request_cache()
    def unauthenticated_userid(self, request):
        """ Get the unauthenticated user id """

        policy = self.get_policy(request)
        return policy.unauthenticated_userid(request)


def auth_fake_user_tween_factory(handler, registry):
    """
    Tween that adds a fake user to environ to simulate remote user based
    authentication.
    """

    settings = registry.settings
    username = settings['auth']['policy:remote']['fake_user']

    def auth_fake_user_tween(request):
        # Add fake user as REMOTE_USER if requested
        environ = request.environ
        environ['REMOTE_USER'] = username

        # Set the authentication policy
        request.authentication_policy = 'remote'

        return handler(request)

    return auth_fake_user_tween


def auth_header_user_tween_factory(handler, registry):
    """
    Tween that adds remote user from header
    This is useful when application is behind a proxy that handles authentication
    """

    settings = registry.settings
    header = settings['auth']['policy:remote']['header']

    def auth_header_user_tween(request):
        if header in request.headers:
            request.environ['REMOTE_USER'] = request.headers[header]

        return handler(request)

    return auth_header_user_tween


def check_credentials(username, password, request, principals=True):
    """ Check username and password using configured backend """

    params = get_settings(request, 'auth', 'auth')

    with BACKENDS[params['backend']] as backend:
        if not backend.validate_password(request, username, password):
            if principals:
                return None

            return False

    # Principals
    if not principals:
        return True

    callback = params['callback']
    return callback(username, request)


def extract_token(request):
    """ Extract authentication token from request """

    params = get_settings(request, 'auth', 'policy:token')

    if params.get('query_param'):
        return request.GET.get(params['query_param'])

    if params.get('header'):
        token = request.headers.get(params['header'])
        if token is None:
            return None

        if not params.get('scheme'):
            return token

        try:
            scheme, token = token.split(' ', 1)
        except ValueError:  # not enough values to unpack
            return None

        if scheme.lower() != params['scheme'].lower():
            return None

        return token

    return None


def get_user_by_username(request, username):
    """ Wrapper to get_user_by_username function defined in settings """

    params = get_settings(request, 'auth', 'auth')
    func = params['get_user_by_username']

    return func(request, username)


def on_before_renderer(event):
    """ Add authenticated_user and has_permission() to renderer context """

    request = event['request']

    event['authentication_policy'] = request.authentication_policy
    event['authenticated_user'] = request.authenticated_user
    event['has_permission'] = request.has_permission


def on_new_request(event):
    """ Add authenticated_user to request """

    request = event.request
    request.authenticated_user = get_user_by_username(request, request.authenticated_userid)

    if not hasattr(request, 'authentication_policy'):
        request.authentication_policy = None


def includeme(config):
    """
    Set up standard configurator registrations. Use via:

    .. code-block:: python

    config = Configurator()
    config.include('pyramid_helpers.auth')
    """

    config.add_subscriber(on_before_renderer, 'pyramid.events.BeforeRender')
    config.add_subscriber(on_new_request, 'pyramid.events.NewRequest')

    # Load an parse settings
    settings = get_settings(config, 'auth')
    if settings is None:
        raise ConfigurationError('[AUTH] Invalid or missing configuration for AUTH, please check auth.filepath directive')

    settings = parse_settings(settings, SETTINGS_RULES, defaults=SETTINGS_DEFAULTS)

    def resolve_func(section, key):
        func = resolve_dotted(settings[section][key])
        if func is None or not callable(func):
            raise ConfigurationError(f'[AUTH] Invalid value for parameter {key} in section [{section}]: {settings[section][key]}')

        settings[section][key] = func
        return func

    # Register database backend
    backend = DatabaseAuthenticationBackend()
    backend.setup()

    # Check backend
    if settings['auth']['backend'] is None:
        raise ConfigurationError('[AUTH] Missing value for parameter backend in section [auth]')

    if settings['auth']['backend'] not in BACKENDS:
        raise ConfigurationError(f'[AUTH] Invalid value for parameter backend in section [auth]: {settings["auth"]["backend"]}')

    # Resolve callback
    callback = resolve_func('auth', 'callback')

    # Resolve get_user_by_username
    resolve_func('auth', 'get_user_by_username')

    # Check policies
    policies = {}

    if 'all' in settings['auth']['policies']:
        settings['auth']['policies'] = MultiSecurityPolicy.POLICIES[:]
    else:
        for policy in settings['auth']['policies']:
            if policy not in MultiSecurityPolicy.POLICIES:
                raise ConfigurationError(f'[AUTH] Invalid policy for parameters policies in section [auth]: {policy}')

    if 'basic' in settings['auth']['policies']:
        resolve_func('policy:basic', 'identify')

        policies['basic'] = BasicAuthenticationPolicy(check_credentials, **settings['policy:basic'])

    if 'cookie' in settings['auth']['policies']:
        # Check hashalg
        if settings['policy:cookie']['hashalg'] not in hashlib.algorithms_available:
            raise ConfigurationError(f'[AUTH] Invalid value for parameter hashalg in section [policy:cookie]: {settings["auth"]["policy:cookie"]["hashalg"]}')

        policies['cookie'] = CookieAuthenticationPolicy(callback=callback, **settings['policy:cookie'])

    if 'token' in settings['auth']['policies']:
        identify = resolve_func('policy:token', 'identify')

        policies['token'] = TokenAuthenticationPolicy(callback=callback, identify=identify)

    if 'remote' in settings['auth']['policies']:
        # Add fake user tween if needed
        if settings['policy:remote']['fake_user'] is not None:
            log.warning(
                '[AUTH] POLICY `remote` IS ENABLED WITH `fake_user` SET TO `%s`, USER `%s` WILL BE AUTOMATICALLY CONNECTED WITHOUT ANY AUTHENTICATION, THIS IS VERY DANGEROUS !!!',
                settings['policy:remote']['fake_user'],
                settings['policy:remote']['fake_user']
            )
            config.add_tween('pyramid_helpers.auth.auth_fake_user_tween_factory')

        if settings['policy:remote']['header'] is not None:
            log.warning(
                '[AUTH] POLICY `remote` IS ENABLED WITH `header` SET TO `%s`, UNLESS THE APPLICATION IS BEHIND A PROXY THAT MANAGES THIS HEADER, THIS IS VERY DANGEROUS !!!',
                settings['policy:remote']['header']
            )
            config.add_tween('pyramid_helpers.auth.auth_header_user_tween_factory')

        identify = resolve_func('policy:remote', 'identify')

        policies['remote'] = RemoteUserAuthenticationPolicy(callback=callback, identify=identify)

    # Set security policy
    config.set_security_policy(MultiSecurityPolicy(policies))

    log.info('[AUTH] Initialization complete: policies=%s, backend=%s', settings['auth']['policies'], settings['auth']['backend'])
