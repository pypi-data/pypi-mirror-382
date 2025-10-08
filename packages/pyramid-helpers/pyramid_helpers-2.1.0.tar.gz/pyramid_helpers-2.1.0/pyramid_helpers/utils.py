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

""" Utils functions for Pyramid """

from configparser import ConfigParser
from configparser import Error
import datetime
import importlib
import logging
import os
import re
import secrets
import string
import warnings
import zoneinfo

from beaker.util import verify_rules
from decorator import decorator

from pyramid.request import Request
from pyramid.request import RequestLocalCache


RANDOM_STRING = string.ascii_letters + string.digits
TIMEZONE = 'Europe/Paris'


log = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """ Configuration error """


def compute_session_key(request, section, name):
    """ Compute unique session key for data persistence """

    predicates = '({})'.format(
        ', '.join(
            f'{predicate}={value}'
            for predicate, value in sorted(request.matchdict.items())
        )
    ) if request.matchdict else ''

    return f'[{section}] {request.matched_route.name}{predicates}::{name}'


def deprecated(old_name, new_func, new_name=None):
    """ Display a deprecation warning when function is called """

    def wrapper(*args, **kwargs):
        warnings.warn(
            f'`{wrapper.__old_name__}()` is deprecated and will be removed soon; use `{wrapper.__new_name__}()',
            DeprecationWarning,
            stacklevel=2,
        )
        return wrapper.__new_func__(*args, **kwargs)

    wrapper.__old_name__ = old_name
    wrapper.__new_func__ = new_func
    wrapper.__new_name__ = new_name or new_func.__name__

    return wrapper


def request_cache():
    """
    Cache decorator

    Values are cached during the lifecycle of a request with a `RequestLocalCache()` instance.

    Warning: The store key is computed from `Request` instance **only**. Other arguments are transparent for caching operation.
    """

    cache = RequestLocalCache()

    def wrapper(func, *args, **kwargs):
        """ Decorator Wrapper function """

        # Get request object from args
        # First arg is «self» when func is a method
        request = get_instance_from_args(args)

        # pylint: disable=unused-argument
        def creator(request):
            func.cache = cache
            return func(*args, **kwargs)

        return cache.get_or_create(request, creator=creator)

    return decorator(wrapper)


def on_before_renderer(event):
    """ Add utc<->local datetime converters to context """

    request = event['request']

    event['localize'] = request.localize
    event['localtoutc'] = request.localtoutc
    event['utctolocal'] = request.utctolocal


def on_new_request(event):
    """ Add utc<->local datetime converters to request """

    request = event.request

    def localize(dt):
        tzinfo = get_tzinfo(request)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=tzinfo)
        else:
            dt = dt.astimezone(tzinfo)

        return dt

    request.localize = localize

    def localtoutc(dt):
        tzinfo = get_tzinfo(request)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=tzinfo)

        return dt.astimezone(datetime.timezone.utc)

    request.localtoutc = localtoutc

    def utctolocal(dt):
        tzinfo = get_tzinfo(request)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)

        return dt.astimezone(tzinfo)

    request.utctolocal = utctolocal


def get_instance_from_args(args, cls=Request):
    """ Return first `cls` instance found in args, raise ValueError otherwise """

    for arg in args:
        if isinstance(arg, cls):
            return arg

    raise ValueError(f'Missing {cls.__name__} object in args list')


def get_settings(obj, key, section=None):
    """
    Get settings from key
    If key is missing, try to load settings from `key.filepath` INI file
    """

    registry = obj.registry
    settings = registry.settings

    if key not in settings:
        # Load settings from file
        filepath = settings.get(f'{key}.filepath')
        if filepath is None:
            log.debug('Missing %s.filepath directive, please check configuration file', key)
            return None

        filepath = os.path.abspath(filepath)
        if not os.path.isfile(filepath):
            log.error('Invalid %s.filepath directive, please check configuration file', key)
            return None

        if not os.access(filepath, os.R_OK):
            log.error('Not enough permission to access file %s', filepath)
            return None

        parser = ConfigParser(defaults={'here': os.path.dirname(filepath)})
        parser.optionxform = str    # Be case sensitive

        try:
            parser.read(filepath)

            settings[key] = {
                section: dict(parser.items(section))
                for section in parser.sections()
            }
        except (IOError, Error):
            log.exception('Failed to read file %s', filepath)
            return None

    if section is None:
        return settings[key]

    return settings[key].get(section) or {}


@request_cache()
def get_tzinfo(request):
    """ Get timezone object """

    available_timezones = zoneinfo.available_timezones()

    # Try to get timezone from authenticated user
    if getattr(request, 'authenticated_user', None) is not None:
        timezone = getattr(request.authenticated_user, 'timezone', None)
    else:
        timezone = None

    if timezone is None or timezone not in available_timezones:
        # Falling back to timezone from settings
        registry = request.registry
        settings = registry.settings

        timezone = settings.get('timezone')

    if timezone is None or timezone not in available_timezones:
        # Use default timezone
        timezone = TIMEZONE

    return zoneinfo.ZoneInfo(timezone)


def parse_settings(settings, rules, defaults=None):
    """ Parse and check settings """

    if defaults:
        for regex, options in defaults.items():
            found = False
            for section in settings:
                if not re.match(f'^{regex}$', section):
                    continue

                found = True

                for option, value in options.items():
                    settings[section].setdefault(option, value)

            if found or ':' in regex:
                continue

            settings[regex] = options.copy()

    for section in settings:
        settings[section].pop('here', None)

        for regex, rules_data in rules.items():
            if re.match(f'^{regex}$', section):
                verify_rules(settings[section], rules_data)
                break

    return settings


def random_string(length=10):
    """ Get a random string """

    return ''.join(
        secrets.choice(RANDOM_STRING)
        for _ in range(length)
    )


def resolve_dotted(dotted):
    """ Resolve dotted string to module attribute """

    if not dotted:
        return None

    module_name, module_attr = dotted.rsplit('.', 1)
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        return None

    return getattr(module, module_attr)


def includeme(config):
    """
    Set up standard configurator registrations. Use via:

    .. code-block:: python

    config = Configurator()
    config.include('pyramid_helpers.utils')
    """

    # Subscribers setup
    config.add_subscriber(on_before_renderer, 'pyramid.events.BeforeRender')
    config.add_subscriber(on_new_request, 'pyramid.events.NewRequest')
