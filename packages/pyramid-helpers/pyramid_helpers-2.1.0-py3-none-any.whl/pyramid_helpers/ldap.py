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

""" LDAP client for Pyramid-Helpers """

import logging
import pprint
import threading
import time

from beaker.cache import Cache
from beaker.util import NoneType
from beaker.util import parse_cache_config_options

import ldap
import ldap.controls
import ldap.modlist

from pyramid_helpers.auth import AuthenticationBackend
from pyramid_helpers.utils import ConfigurationError
from pyramid_helpers.utils import get_settings
from pyramid_helpers.utils import parse_settings


SETTINGS_DEFAULTS = {
    'ldap': {
        'tls': False,
        'ca_certs': None,
        'certfile': None,
        'keyfile': None,
        'auth_base_dn': None,
        'auth_filter': 'uid={0}',
        'base_dn': None,
        'bind_dn': None,
        'bind_credential': None,
        'max_retry': 5,
        'retry_after': 300,
        'timeout': 2.0,
    },
}

SETTINGS_RULES = {
    'ldap': [
        ('uri', (str, NoneType), 'uri must be a string designating valid uri'),
        ('tls', (bool, NoneType), 'tls must be a boolean or an integer'),
        ('ca_certs', (str, NoneType), 'ca_certs must be a string designating a filepath'),
        ('certfile', (str, NoneType), 'certfile must be a string designating a filepath'),
        ('keyfile', (str, NoneType), 'keyfile must be a string designating a filepath'),
        ('auth_base_dn', (str, NoneType), 'auth_base_dn must be a string designating a valid dn'),
        ('auth_filter', (str, NoneType), 'auth_filter must be a string designating a valid filter'),
        ('base_dn', (str, NoneType), 'base_dn must be a string designating a valid dn'),
        ('bind_dn', (str, NoneType), 'bind_dn must be a string designating a valid dn'),
        ('bind_credential', (str, NoneType), 'bind_credential must be a string designating a valid credential'),
        ('max_retry', (int, ), 'max_retry must be a string designating a valid integer'),
        ('retry_after', (int, ), 'retry_after must be a string designating a valid integer'),
        ('timeout', (float, ), 'timeout must be a string designating a valid float'),
    ],
}


log = logging.getLogger(__name__)

client = None


class LDAPClient(AuthenticationBackend):
    """ LDAP authentication client """

    # pylint: disable=no-member

    __name__ = 'ldap'

    def __init__(self):
        """ LDAP initialization """

        self.uri = None

        self.tls = False
        self.ca_certs = None
        self.certfile = None
        self.keyfile = None

        self.auth_base_dn = None
        self.auth_filter = None
        self.base_dn = None

        self.__bind_dn = None
        self.__bind_credential = None
        self.__cache = None

        self.__conn = None
        self.__lock = threading.Lock()

        # Error handling
        self.max_retry = 5
        self.retry_after = 300
        self.timeout = 2.0

        self.fail_count = 0
        self.wait_until = None

    def __enter__(self):
        """ Acquire lock """

        # pylint: disable=consider-using-with
        self.__lock.acquire()

        return self

    def __exit__(self, type_, value, traceback):
        """ Release lock and close connection """

        self.unbind()
        self.__lock.release()

    def __on_error(self, message, level=logging.ERROR, **kwargs):

        self.fail_count += 1

        if self.fail_count >= self.max_retry:
            self.fail_count = 0
            self.wait_until = time.time() + self.retry_after

            msg = '[LDAP] %s, max failure count was reached (%s), waiting for %s seconds before attempting new connection'
            args = (self.max_retry, self.retry_after)
        else:
            msg = '[LDAP] %s, retry=%s, remaining=%s'
            args = (self.fail_count, self.max_retry - self.fail_count)

        log.log(level, msg, message, *args, **kwargs)

    def add(self, dn, attrs):
        """ Add a new object to LDAP """

        if not self.bind(self.__bind_dn, self.__bind_credential):
            return False

        # Get ldif object suitable for ldap.add()
        ldif = ldap.modlist.addModlist(attrs)
        try:
            # Create LDAP object
            self.__conn.add_s(dn, ldif)
        except ldap.LDAPError:
            log.exception('[LDAP] Failed to create object dn=%s, ldif was:\n%s', dn, pprint.pformat(ldif))
            return False

        log.info('[LDAP] Created object dn=%s.', dn)
        return True

    def bind(self, dn, credential, force=False):
        """ Initialize LDAP connection """

        if not self.__lock.locked():
            raise ldap.LDAPError('Please use LDAPClient inside a `with` statement')

        if self.__conn is not None and not force:
            return True

        if self.wait_until and self.wait_until > time.time():
            return False

        self.wait_until = None

        try:
            self.__conn = ldap.initialize(self.uri)

            self.__conn.set_option(ldap.OPT_NETWORK_TIMEOUT, self.timeout)
            self.__conn.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3)
            self.__conn.set_option(ldap.OPT_TIMEOUT, self.timeout)

            if self.ca_certs:
                self.__conn.set_option(ldap.OPT_X_TLS_CACERTFILE, self.ca_certs)

            if self.certfile and self.keyfile:
                self.__conn.set_option(ldap.OPT_X_TLS_CERTFILE, self.certfile)
                self.__conn.set_option(ldap.OPT_X_TLS_KEYFILE, self.keyfile)

            if self.ca_certs or (self.certfile and self.keyfile):
                # Apply pending TLS settings and create a new internal TLS context
                self.__conn.set_option(ldap.OPT_X_TLS_NEWCTX, 0)

            if self.tls:
                self.__conn.start_tls_s()

            if dn and credential:
                self.__conn.simple_bind_s(dn, credential)

        except ldap.INVALID_CREDENTIALS:
            log.error('[LDAP] Authentication failed (%s)', dn)
            return False

        except ldap.LDAPError:
            self.__on_error('Failed to connect to remote server', exc_info=1)
            return False

        # Success
        self.fail_count = 0

        return True

    def get(self, dn, attrlist=None, force=False):
        """ Get an object from it's DN """

        result = self.search(attrlist=attrlist, dn=dn, force=force)
        if not result:
            return None

        return result[0]

    def delete(self, dn):
        """ Delete an object from LDAP """

        if not self.bind(self.__bind_dn, self.__bind_credential):
            return False

        try:
            self.__conn.delete_s(dn)
        except ldap.LDAPError:
            log.exception('[LDAP] Failed to delete object dn=%s.', dn)
            return False

        log.info('[LDAP] Deleted object dn=%s.', dn)
        return True

    def modify(self, dn, old_attrs, new_attrs):
        """ Modify an existing object in LDAP """

        if not self.bind(self.__bind_dn, self.__bind_credential):
            return False

        # Get ldif object suitable for ldap.modify()
        ldif = ldap.modlist.modifyModlist(old_attrs, new_attrs, ignore_attr_types=['objectClass', ])
        if not ldif:
            # No modification
            log.debug('[LDAP] Object dn=%s is uptodate', dn)
            return None

        try:
            self.__conn.modify_s(dn, ldif)
        except ldap.LDAPError:
            log.exception('[LDAP] Failed to modify object dn=%s, ldif was:\n%s', dn, pprint.pformat(ldif))
            return False

        log.info('[LDAP] Modified object dn=%s.', dn)
        return True

    def search(self, attrlist=None, base_dn=None, dn=None, filterstr='(objectClass=*)', force=False):
        """ Search entries in LDAP """

        if dn is None:
            if base_dn is None:
                base_dn = self.base_dn
            scope = ldap.SCOPE_SUBTREE
        else:
            base_dn = dn
            scope = ldap.SCOPE_BASE

        cache_key = f'{base_dn}::{filterstr}::{attrlist!r}'

        if not force and self.__cache is not None:
            try:
                return self.__cache[cache_key]
            except KeyError:
                pass

        if not self.bind(self.__bind_dn, self.__bind_credential):
            return None

        try:
            result = self.__conn.search_s(base_dn, scope, filterstr=filterstr, attrlist=attrlist)
        except ldap.NO_SUCH_OBJECT:
            return None
        except ldap.LDAPError:
            self.__on_error('Failed to query remote server', exc_info=1)
            return None

        if self.__cache is not None:
            self.__cache[cache_key] = result

        return result

    def search_iter(self, attrlist=None, base_dn=None, filterstr='(objectClass=*)', size=100):
        """ Search entries in LDAP (paged) """

        if base_dn is None:
            base_dn = self.base_dn

        if not self.bind(self.__bind_dn, self.__bind_credential):
            return

        control = ldap.controls.SimplePagedResultsControl(True, size=size, cookie='')

        while True:
            try:
                msgid = self.__conn.search_ext(base_dn, ldap.SCOPE_SUBTREE, filterstr=filterstr, attrlist=attrlist, serverctrls=[control])
            except ldap.NO_SUCH_OBJECT:
                return
            except ldap.LDAPError:
                self.__on_error('Failed to query remote server', exc_info=1)
                return

            try:
                _, rdata, _, rcontrols = self.__conn.result3(msgid)
            except ldap.LDAPError:
                self.__on_error('Could not pull LDAP results', exc_info=1)
                break

            # Yield result
            for dn, attrs in rdata:
                yield (dn, attrs)

            # Get page control from returned controls
            for rcontrol in rcontrols:
                if rcontrol.controlType == ldap.CONTROL_PAGEDRESULTS:
                    break
            else:
                self.__on_error('Server ignores RFC 2696 control')
                break

            # pylint: disable=undefined-loop-variable
            if not rcontrol.cookie:
                # No more result
                break

            control.cookie = rcontrol.cookie

    def setup(self, *args, **kwargs):
        """
        LDAP client setup

        :param uri: URI to connect to
        :param tls: Boolean, enable TLS connectiion
        :param ca_certs: String, path to file with PEM encoded CA certs
        :param certfile: String, path to file with PEM encoded cert for client cert authentication
        :param keyfile: String, path to file with PEM encoded key for client cert authentication
        :param auth_base_dn: Base DN for authentication
        :param auth_filter: Filter string for authentication
        :param base_dn: Base DN for searches
        :param bind_dn: Bind DN to use when querying the server
        :param bind_credentiak: Bind credential to use when querying the server
        :param cache: Cache store
        :param max_retry: Integer, maximum retries before stopping to query the server
        :param retry_after: Integer, number of seconds to wait before retrying to query the server
        :param timeout: Float, timeout value for connections
        """

        self.uri = kwargs.get('uri')

        self.tls = kwargs.get('tls', False)
        self.ca_certs = kwargs.get('ca_certs')
        self.certfile = kwargs.get('certfile')
        self.keyfile = kwargs.get('keyfile')

        self.auth_base_dn = kwargs.get('auth_base_dn')
        self.auth_filter = kwargs.get('auth_filter')
        self.base_dn = kwargs.get('base_dn')

        self.__bind_dn = kwargs.get('bind_dn')
        self.__bind_credential = kwargs.get('bind_credential')
        self.__cache = kwargs.get('cache')

        if kwargs.get('max_retry') is not None:
            self.max_retry = kwargs['max_retry']

        if kwargs.get('retry_after') is not None:
            self.retry_after = kwargs['retry_after']

        if kwargs.get('timeout') is not None:
            self.timeout = kwargs['timeout']

        # Calling inherited
        return super().setup(*args, **kwargs)

    def unbind(self):
        """ Close the connection """

        if self.__conn is None:
            return True

        try:
            self.__conn.unbind()

        except ldap.LDAPError:
            self.__on_error('Failed to unbind connection', level=logging.WARNING)
            return False

        finally:
            self.__conn = None

        return True

    def validate_password(self, request, username, password):
        """ Attempt to bind with the LDAP server using simple authentication """

        if not ldap.dn.is_dn(username):
            if self.auth_filter is None:
                # Configuration error
                log.error('[LDAP] Username must either be dn or auth_filter must be set when calling `.validate_password()`')
                return False

            result = self.search(filterstr=self.auth_filter.format(username), base_dn=self.auth_base_dn)
            if not result:
                # Invalid user
                return False

            username = result[0][0]

        self.unbind()

        return self.bind(username, password)


# Create client object
client = LDAPClient()


def includeme(config):
    """ LDAP module initialization """

    # Load and parse settings
    settings = get_settings(config, 'ldap')
    if settings is None:
        raise ConfigurationError('[LDAP] Invalid or missing configuration for LDAP, please check ldap.filepath directive')

    settings = parse_settings(settings, SETTINGS_RULES, defaults=SETTINGS_DEFAULTS)

    # Connection
    if settings['ldap']['uri'] is None:
        raise ConfigurationError('[LDAP] Missing uri parameter in configuration')

    # Cache setup
    cache_params = parse_cache_config_options({
        f'cache.{k}': v
        for k, v in settings['cache'].items()
    }) if 'cache' in settings else {'enabled': False}

    if cache_params['enabled']:
        cache = Cache('ldap', **cache_params)
    else:
        cache = None

    # Prepare arguments
    kwargs = settings['ldap'].copy()

    # Setup the client
    client.setup(cache=cache, **kwargs)

    log.info('[LDAP] Initialization complete: uri=%s, cache=%s', client.uri, 'yes, type={type}, expire={expire}'.format(**cache_params) if cache else 'no')
