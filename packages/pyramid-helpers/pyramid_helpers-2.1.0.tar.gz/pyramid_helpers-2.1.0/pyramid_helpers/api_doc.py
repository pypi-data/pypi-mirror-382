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

""" API REST interactive documentation view """

import inspect
import logging
import re

from formencode.api import NoDefault

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.security import NO_PERMISSION_REQUIRED


log = logging.getLogger(__name__)

DECORATOR_RE = re.compile(r'^@(?P<func>paginate|validate)\((?P<args>.+)?\)$')

PAGER_PARAMS = {
    'sort': {
        'description': 'Sorting key',
        'type': 'UnicodeString',
    },
    'order': {
        'description': 'Sorting order',
        'type': 'OneOf',
        'values': ['asc', 'desc']
    },
    'limit': {
        'description': 'Number of items per page',
        'type': 'OneOf',
    },
    'page': {
        'description': 'Page number',
        'type': 'Int',
        'default': 1,
    },
}


def datetime_format_python_to_moment(format_):
    """ Convert python datetime format (C Standard 1989) into Moment.js datetime format """

    # year 4 digits
    format_ = format_.replace('%Y', 'YYYY')
    # month 2 digits
    format_ = format_.replace('%m', 'MM')
    # day 2 digits
    format_ = format_.replace('%d', 'DD')
    # hours 2 digits (24h)
    format_ = format_.replace('%H', 'HH')
    # hours 2 digits (12h)
    format_ = format_.replace('%I', 'hh')
    # hours AM/PM
    format_ = format_.replace('%p', 'A')
    # minutes 2 digits
    format_ = format_.replace('%M', 'mm')
    # seconds 2 digits
    format_ = format_.replace('%S', 'ss')

    return format_


def inspect_schema_doc(tree, parameters, parent=None):
    """ Inspect `formencode.Schema` documentation """

    if not parameters:
        return

    if isinstance(tree, list):
        for node in tree:
            inspect_schema_doc(node, parameters)
        return

    if tree[0].__name__ in ('object', 'Declarative') or tree[0].__module__.startswith('formencode'):
        return

    doc = inspect.getdoc(tree[0])
    for line in doc.split('\n'):
        if not line.startswith(':param'):
            continue

        line = line.split(':', 2)
        if len(line) != 3:
            continue

        name = line[1].split(' ')[-1].strip()
        if parent is not None:
            name = f'{parent}.{name}'
        if name in parameters:
            parameters[name]['description'] = line[2].strip()


def inspect_validator(validator, name=None):
    """ Inspect `formencode.validators.FancyValidator` """

    data = {
        'description': None,
    }

    if name is not None:
        data['name'] = name
        data['required'] = validator.not_empty is True
        data['parameter_type'] = 'query'

    if_empty = None
    if validator.if_empty is not None and validator.if_empty is not NoDefault:
        if_empty = validator.if_empty
    if_missing = None
    if validator.if_missing is not None and validator.if_missing is not NoDefault:
        if_missing = validator.if_missing
    data['default'] = if_missing or if_empty

    class_name = validator.__class__.__name__
    if class_name.endswith('Validator'):
        class_name = class_name.replace('Validator', '')

    data['type'] = class_name
    if class_name == 'OneOf':
        data['values'] = validator.list
    elif class_name in ('ForEach', 'NumberList', 'StringList'):
        data['items'] = inspect_validator(validator.validators[0]) if validator.validators else None
    elif class_name in ('Int', 'Number'):
        data['min'] = validator.min
        data['max'] = validator.max
    elif data['type'] == 'DateTime':
        if validator.is_date:
            data['type'] = 'Date'
        data['format'] = datetime_format_python_to_moment(validator.format)

    return data


# from CPython project
# https://hg.python.org/cpython/file/tip/Lib/inspect.py
def unwrap(func, stop=None):
    """Get the object wrapped by *func*.

    Follows the chain of :attr:`__wrapped__` attributes returning the last
    object in the chain.

    *stop* is an optional callback accepting an object in the wrapper chain
    as its sole argument that allows the unwrapping to be terminated early if
    the callback returns a true value. If the callback never returns a true
    value, the last object in the chain is returned as usual. For example,
    :func:`signature` uses this to stop unwrapping if any object in the
    chain has a ``__signature__`` attribute defined.

   :exc:`ValueError` is raised if a cycle is encountered.

    """
    if stop is None:
        def _is_wrapper(func):
            return hasattr(func, '__wrapped__')
    else:
        def _is_wrapper(func):
            return hasattr(func, '__wrapped__') and not stop(func)

    # remember the original func for error reporting
    func_ = func

    # Memoise by id to tolerate non-hashable objects
    memo = {id(func_)}
    while _is_wrapper(func):
        func = func.__wrapped__
        id_func = id(func)
        if id_func in memo:
            raise ValueError('wrapper loop when unwrapping {!r}'.format(func_))
        memo.add(id_func)

    return func


def api_doc(request, renderer_values):
    """Render API documentation

    Args:
        request (obj): currently active request.
        renderer_values (dict): values passed to renderer.
            breadcrumb: Page breadcrumb
            hide_undocumented: True to hide undocumented services (default False)
            title: Page title
            subtitle: Page subtitle

    Returns:
        unicode: HTML response body.

    """

    registry = request.registry
    settings = registry.settings
    translate = request.translate

    introspector = registry.introspector

    # Get defined routes
    services = {}

    for item in introspector.get_category('routes'):
        introspectable = item['introspectable']
        route_name = introspectable.discriminator

        if not route_name.startswith('api.'):
            continue

        route_intr = introspector.get('routes', route_name)
        route = route_intr['object']

        services[route_name] = {
            'allowed': True,
            'doc': None,
            'module': None,
            'name': route_name,
            'pattern': request.script_name + route_intr['pattern'],
            'parameters': [],
            'request_methods': route_intr['request_methods'],
        }

        # get custom predicates
        custom_predicates = []
        for predicate in route.predicates:
            if predicate.__class__.__name__ == 'EnumPredicate':
                param_type = 'OneOf'
            elif predicate.__class__.__name__ == 'NumericPredicate':
                param_type = 'Int'
            else:
                continue

            for name in predicate.names:
                param_data = {
                    'name': name,
                    'type': param_type,
                    'parameter_type': 'path',
                    'required': True,
                    'default': None,
                    'description': None,
                }

                if predicate.__class__.__name__ == 'EnumPredicate':
                    param_data['values'] = predicate.params[name]

                services[route_name]['parameters'].append(param_data)

                custom_predicates.append(name)

        # get other predicates (not custom) present in pattern
        for name in route.match(route_intr['pattern']).keys():
            if name not in custom_predicates:
                services[route_name]['parameters'].append({
                    'name': name,
                    'type': 'ByteString',
                    'parameter_type': 'path',
                    'required': True,
                    'default': None,
                    'description': None,
                })

    # Check permission
    for item in introspector.get_category('permissions'):
        introspectable = item['introspectable']
        permission = introspectable.discriminator
        if permission == NO_PERMISSION_REQUIRED:
            continue

        for introspectable_view in item['related']:
            route_name = introspectable_view['route_name']
            if route_name in services:
                services[route_name]['allowed'] = bool(request.has_permission(permission))

    # Get associated views
    modules = {}

    for item in introspector.get_category('views'):
        introspectable = item['introspectable']
        route_name = introspectable['route_name']
        view = introspectable['callable']

        service = services.get(route_name)
        if service is None:
            continue

        if introspectable['request_methods']:
            if isinstance(introspectable['request_methods'], tuple):
                service['request_methods'] = introspectable['request_methods']
            else:
                service['request_methods'] = (introspectable['request_methods'],)

        callable_func = unwrap(view)

        __globals__ = callable_func.__globals__
        module_name = __globals__['__name__']

        if module_name not in modules:
            modules[module_name] = {
                'doc': callable_func.__globals__['__doc__'].strip(),
                'services': [],
            }
        modules[module_name]['services'].append(service)

        service['module'] = module_name
        if callable_func.__doc__:
            service['doc'] = callable_func.__doc__.strip()

        source_lines, _ = inspect.getsourcelines(callable_func)
        for line in source_lines:
            if line.startswith('def '):
                break

            # Extract decorator parameters
            match = DECORATOR_RE.match(line)
            if match is None:
                continue

            decorator_name, params_str = match.groups()

            def __extract__(*args, **kwargs):
                __extract__.args = args         # pylint: disable=cell-var-from-loop
                __extract__.kwargs = kwargs     # pylint: disable=cell-var-from-loop

            globals_ = __globals__.copy()
            globals_['__extract__'] = __extract__

            # pylint: disable=eval-used
            eval(f'__extract__({params_str})', globals_)

            if decorator_name == 'paginate':
                pager_name = __extract__.args[0]

                for param_name, param_data in PAGER_PARAMS.items():
                    param_data = param_data.copy()

                    param_data.update({
                        'name': f'{pager_name}.{param_name}',
                        'required': False,
                        'parameter_type': 'query (paging)',
                    })

                    if param_name in __extract__.kwargs:
                        param_data['default'] = __extract__.kwargs[param_name]
                    elif 'default' not in param_data:
                        param_data['default'] = None

                    if param_name == 'limit':
                        param_data['values'] = __extract__.kwargs.get('limits', settings['pagers.limits'])

                    service['parameters'].append(param_data)

            elif decorator_name == 'validate':
                schema = __extract__.args[1]

                parameters = {}
                for name, field in schema.fields.items():
                    class_name = field.__class__.__name__
                    if class_name.endswith('Schema'):
                        for sub_name, sub_field in field.__dict__['fields'].items():
                            parameter_name = f'{name}.{sub_name}'
                            parameters[parameter_name] = inspect_validator(sub_field, parameter_name)

                        inspect_schema_doc((field.__class__,), parameters, name)
                    else:
                        parameters[name] = inspect_validator(field, name)

                inspect_schema_doc(inspect.getclasstree(schema.__mro__, unique=True), parameters)

                # sort parameters by type and name
                service['parameters'] += sorted(parameters.values(), key=lambda param_data: (param_data['type'], param_data['name']))

    # Orphan routes
    orphans = [
        service
        for service in services.values()
        if service['module'] is None
    ]

    # Get Bootstrap version
    bootstrap_version = settings.get('api_doc.bootstrap_version', None)
    if bootstrap_version is None:
        raise HTTPBadRequest(detail=translate('Missing `api_doc.bootstrap_version` entry in configuration.'))

    bootstrap_version = bootstrap_version.split('.')[0]
    if bootstrap_version == '3':
        required_libraries = ('bootstrap-datetimepicker', 'font-awesome', 'moment')
    elif bootstrap_version in ('4', '5'):
        required_libraries = ('easepick', 'font-awesome', 'moment')
    else:
        raise HTTPBadRequest(detail=translate('Unsupported Bootstrap version: {0}').format(bootstrap_version))

    # Get libraries
    options = {
        option[18:]: settings[option]
        for option in settings
        if option.startswith('api_doc.libraries.')
    }

    libraries = []
    for library in options:
        for value in options[library].split():
            if value.startswith(('http://', 'https://', '//')):
                libraries.append(value)
            elif value != 'site':
                libraries.append(request.static_path(value))

    missing = set(required_libraries).difference(options)

    # Set template according to Bootstrap version
    request.override_renderer = f'/api-doc-bs{bootstrap_version}.mako'

    # Update renderer values
    renderer_values.update({
        'libraries': libraries,
        'missing': missing,
        'modules': modules,
        'orphans': orphans,
    })

    return renderer_values
