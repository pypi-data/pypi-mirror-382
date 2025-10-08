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

""" Custom renderers for Pyramid-Helpers """

import csv
import io
import json
from logging import getLogger

from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.settings import asbool


log = getLogger(__name__)


# pylint: disable=unused-argument
def csv_renderer_factory(info):
    """ CSV renderer for Pyramid """

    def _render(value, system):
        request = system.get('request')
        translate = request.translate

        # Get parameters
        encoding = value.pop('encoding', 'utf-8')
        filename = value.pop('filename', 'result.csv')
        rows = value.pop('rows', None) or []

        # Create CSV
        try:
            fp = io.StringIO()

            writer = csv.writer(fp, **value)
            writer.writerows(rows)

        except Exception as exc:
            log.exception('Could not convert view response to CSV')
            raise HTTPInternalServerError(detail=translate('Could not convert view response to CSV')) from exc

        # Set content type
        request.response.content_type = f'text/csv; charset="{encoding}"'
        request.response.content_disposition = f'attachment; filename="{filename}"'

        # Return file content
        fp.seek(0)
        content = fp.read()
        return content.encode(encoding)

    return _render


# pylint: disable=unused-argument
def json_renderer_factory(info):
    """ Custom JSON renderer with callback support """

    def _render(value, system):
        request = system.get('request')
        registry = request.registry
        settings = registry.settings

        # Prepare options
        kwargs = {
            k[15:]: v
            for k, v in settings.items()
            if k.startswith('renderers.json.')
        }

        kwargs.pop('enabled')

        if 'indent' in kwargs:
            kwargs['indent'] = int(kwargs['indent'])

        for key in ('skipkeys', 'ensure_ascii', 'check_circular', 'allow_nan', 'sort_keys'):
            if key in kwargs:
                kwargs[key] = asbool(kwargs[key])

        # Extract callback from query
        callback = kwargs.pop('callback', None)
        if callback:
            callback = request.params.get(callback)

        result = json.dumps(value, default=str, **kwargs)

        if callback:
            request.response.content_type = 'application/javascript; charset="utf-8"'
            result = f'{callback}({result})'
        else:
            request.response.content_type = 'application/json; charset="utf-8"'

        return result

    return _render


def includeme(config):
    """
    Set up standard configurator registrations. Use via:

    .. code-block:: python

    config = Configurator()
    config.include('pyramid_helpers.renderers')
    """

    registry = config.registry
    settings = registry.settings

    if asbool(settings.get('renderers.csv.enabled')):
        # Add CSV renderer
        config.add_renderer('csv', csv_renderer_factory)

    if asbool(settings.get('renderers.json.enabled')):
        # Replace JSON renderer (callback support)
        config.add_renderer('json', json_renderer_factory)
