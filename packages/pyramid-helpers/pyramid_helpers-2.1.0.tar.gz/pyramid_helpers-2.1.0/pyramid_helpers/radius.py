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

""" Radius client for Pyramid-Helpers """

from io import StringIO
import logging
import threading
import time

from beaker.util import NoneType

from pyrad.client import Client
from pyrad.client import Timeout
from pyrad.dictionary import Dictionary
from pyrad.packet import AccessAccept
from pyrad.packet import AccessRequest

from pyramid_helpers.auth import AuthenticationBackend
from pyramid_helpers.utils import ConfigurationError
from pyramid_helpers.utils import get_settings
from pyramid_helpers.utils import parse_settings


SETTINGS_DEFAULTS = {
    'radius': {
        'enabled': False,
        'retries': 2,
        'timeout': 3.0,
    },
    r'server:\d+': {
        'enabled': True,
        'acctport': 1813,
        'authport': 1812,
        'coaport': 3799,
    },
}

SETTINGS_RULES = {
    r'attr:\d+': [
        ('name', (str, ), 'name must be a string designating valid attribute name'),
        ('type', (str, ), 'type must be a string designating valid attribute type'),
    ],
    'radius': [
        ('enabled', (bool, NoneType), 'enabled must be a boolean or an integer'),
        ('retries', (int, ), 'retries must be a string designating a valid integer'),
        ('timeout', (float, ), 'timeout must be a string designating a valid float'),
    ],
    r'server:\d+': [
        ('enabled', (bool, NoneType), 'enabled must be a boolean or an integer'),
        ('server', (str, ), 'server must be a string designating valid server'),
        ('secret', (str, ), 'secret must be a string designating a valid secret'),
        ('authport', (int, ), 'authentication port must be an integer'),
        ('acctport', (int, ), 'accounting port must be an integer'),
        ('coaport', (int, ), 'CoA port must be an integer'),
    ],
}


log = logging.getLogger(__name__)

client = None


class RadiusError(Exception):
    """ RADIUS error """


class RadiusClient(AuthenticationBackend):
    """ RADIUS authentication client """

    __name__ = 'radius'

    def __init__(self):
        """ RADIUS initialization """

        self.dictionary = None
        self.retries = None
        self.servers = []
        self.timeout = None

        self.__lock = threading.Lock()

    def __enter__(self):
        """ Acquire lock """

        # pylint: disable=consider-using-with
        self.__lock.acquire()

        return self

    def __exit__(self, type_, value, traceback):
        """ Release lock """

        self.__lock.release()

    def setup(self, *args, **kwargs):
        """
        RADIUS client setup

        :param servers: List or server settings to connect to
        :param attributes: Attributes to use
        :param retries: Integer, maximum retries before stopping to query the server
        :param timeout: Float, timeout value for connections
        """

        # Prepare dictionary
        self.dictionary = []

        attributes = kwargs.pop('attributes', None) or []
        for data in attributes:
            flags = data.get('flags')
            self.dictionary.append('ATTRIBUTE {name:20s} {oid:5d} {type:10s}{0}'.format(' {0}'.format(flags) if flags else '', **data))

        # Prepare clients settings
        self.servers = kwargs.pop('servers', None) or []

        if kwargs.get('retries'):
            self.retries = kwargs.pop('retries')

        if kwargs.get('timeout'):
            self.timeout = kwargs.pop('timeout')

        # Calling inherited
        return super().setup(*args, **kwargs)

    # pylint: disable=unused-argument
    def validate_password(self, request, username, password):
        """ Attempt to send an authentication packet to servers """

        if not self.__lock.locked():
            raise RadiusError('Please use RadiusClient inside a `with` statement')

        now = time.time()

        for settings in sorted(self.servers, key=lambda settings: settings.get('date', now)):
            kwargs = settings.copy()
            kwargs.pop('date', None)

            kwargs['dict'] = Dictionary(StringIO('\n'.join(self.dictionary)))

            client_ = Client(**kwargs)

            if self.retries:
                client_.retries = self.retries

            if self.timeout:
                client_.timeout = self.timeout

            req = client_.CreateAuthPacket(code=AccessRequest, username=username)
            req['password'] = req.PwCrypt(password)

            try:
                reply = client_.SendPacket(req)
            except Timeout:
                log.exception('Failed to communicate with RADIUS server (server=%s)', client_.server)
                continue

            client_._CloseSocket()    # pylint: disable=protected-access

            settings['date'] = now

            if reply.code == AccessAccept:
                return True

            # Invalid user
            log.error('[RADIUS] Authentication failed (server=%s, username=%s)', client_.server, username)

        return False


# Create client object
client = RadiusClient()


def includeme(config):
    """ RADIUS module initialization """

    # Load and parse settings
    settings = get_settings(config, 'radius')
    if settings is None:
        raise ConfigurationError('[RADIUS] Invalid or missing configuration for RADIUS, please check radius.filepath directive')

    settings = parse_settings(settings, SETTINGS_RULES, defaults=SETTINGS_DEFAULTS)

    # Settings
    attributes = []
    servers = []

    for section in settings:
        if section.startswith('attr:'):
            data = settings[section].copy()
            try:
                data['oid'] = int(section[5:])
            except ValueError as exc:
                raise ConfigurationError(f'[RADIUS] Invalid attribute definition for {section} in configuration') from exc

            attributes.append(data)

        elif section.startswith('server:'):
            data = settings[section].copy()
            if not data.pop('enabled'):
                continue

            data['secret'] = bytes(data['secret'], 'utf-8')

            servers.append(data)

    if not servers:
        raise ConfigurationError('[RADIUS] Empty or invalid configuration for server entries in configuration')

    # Prepare arguments
    kwargs = settings['radius'].copy()
    kwargs['attributes'] = attributes
    kwargs['servers'] = servers

    # Setup the client
    client.setup(**kwargs)

    log.info('[RADIUS] Initialization complete: servers=%s', ','.join(kwargs['server'] for kwargs in client.servers))
