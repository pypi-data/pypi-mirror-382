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

""" Forms helpers for Pyramid """

from json.decoder import JSONDecodeError
import warnings

from decorator import decorator

from formencode import Invalid
from formencode import validators
from formencode.variabledecode import variable_decode
from formencode.variabledecode import variable_encode

from pyramid_helpers.utils import compute_session_key
from pyramid_helpers.utils import get_instance_from_args

# Monkey patch UnicodeString formencode's validator to always get unicode strings
# See: https://github.com/formencode/formencode/issues/2#issuecomment-12991249
validators.UnicodeString.outputEncoding = None

HTTP_METHODS = {
    'any': ('DELETE', 'GET', 'PATCH', 'POST', 'PUT'),
    'delete': ('DELETE', ),
    'get': ('GET', ),
    'post': ('PATCH', 'POST', 'PUT'),
}


class Form:
    """ Form validation class """

    def __init__(self, name, schema, state, csrf_protect=False, extract='merge', method='post', persistent=False, session_key=None, volatile_items=()):
        """
        @param csrf_protect boolean, set to True is you plan to use CSRF protection
        @param extract string, where to extract data from, one of ('merge', 'get', 'post', 'json'). merge means merging GET and POST.
        @param method string, HTTP method to accept on validate(), one of ('any', 'delete', 'get', 'post'). post also includes PATCH and PUT.
        @param persistent boolean, reuse previous result if no param
        @param session_key string, custom session key for persistent storage, default is a string depending matched route name
        @param volatile_items list of string, list of items that will not be persistent
        """

        if extract not in ('merge', 'get', 'post', 'json'):
            raise ValueError(f'Invalid extract method {extract}')

        if method not in HTTP_METHODS:
            raise ValueError(f'Invalid http method {method}')

        if persistent and method != 'get':
            raise ValueError('Persistent mode is allowed only for get method')

        self.csrf_protect = csrf_protect
        self.extract = extract
        self.method = method
        self.name = name
        self.persistent = persistent
        self.schema = schema
        self.session_key = session_key
        self.state = state
        self.volatile_items = volatile_items

        if self.session_key is None:
            self.session_key = compute_session_key(state.request, 'form', name)

        self.decoded = {}
        self.encoded = {}
        self.errors = {}
        self.params = {}
        self.result = {}
        self.submitted = False
        self.valid = None

    @property
    def csrf_token(self):
        """ Get CSRF token from session """

        if not self.csrf_protect:
            return None
        request = self.state.request
        session = request.session
        return session.get_csrf_token()

    def error(self, name):
        """ Get error message for field """

        return self.errors.get(name)

    # pylint: disable=redefined-outer-name
    def from_python(self, value, validate=False):
        """
        Convert `value` from its Python representation to the foreign
        representation using formencode validator
        """

        request = self.state.request
        session = request.session

        self.decoded = self.schema.from_python(value, self.state)
        self.encoded = variable_encode(self.decoded)

        if not validate:
            return True

        try:
            self.errors = {}
            self.result = self.schema.to_python(self.decoded, self.state)
            self.valid = True

        except Invalid as exc:
            self.errors = exc.unpack_errors(variable_decode)
            self.result = {}
            self.valid = False

        if self.valid and self.persistent:
            # Store params to session
            # Restrict to form data
            session[self.session_key] = {
                k: str(v)
                for k, v in self.encoded.items()
                if k not in self.volatile_items and not k.endswith('--repetitions') and v is not None
            }

            # Load params
            self.params = session[self.session_key]

            # Update request.GET so that things like pagers can work
            request.GET.update(self.params)

        return self.valid

    def to_python(self, value):
        """
        Convert `value` from its foreign representation to its Python
        representation using formencode validator
        """

        try:
            self.errors = {}
            self.result = self.schema.to_python(value, self.state)
            self.decoded = self.schema.from_python(self.result, self.state)
            self.encoded = variable_encode(self.decoded)
            self.valid = True

        except Invalid as exc:
            self.errors = exc.unpack_errors(variable_decode)
            self.result = {}
            self.decoded = value
            self.encoded = variable_encode(self.decoded)
            self.valid = False

        return self.valid

    def validate(self):
        """ Validate request parameters using formencode validator """

        request = self.state.request
        session = request.session
        translate = request.translate

        # Ensure HTTP method is the one that is expected
        if request.method not in HTTP_METHODS[self.method]:
            return None

        # Load params from request
        if self.extract == 'merge':
            self.params = request.params.mixed()

        elif self.extract == 'post':
            self.params = request.POST.mixed()

        elif self.extract == 'json':
            try:
                self.params = request.json_body
            except JSONDecodeError:
                # Invalid JSON content
                self.errors = {'_content': translate('Invalid JSON content')}
                self.params = {}
                self.valid = False
                return False

        else:
            # get
            self.params = request.GET.mixed()

        if self.params:
            # It seems that form has been submitted
            self.submitted = True

        elif self.persistent:
            # Load params from session
            self.params = session.get(self.session_key, {})

            # Update request.GET so that things like pagers can work
            request.GET.update(self.params)

        decoded = variable_decode(self.params)

        if self.csrf_protect and self.csrf_token != decoded.get('_csrf_token'):
            # Invalid CSRF token
            self.errors = {'_csrf_token': translate('Invalid CSRF token')}
            self.result = {}
            self.decoded = decoded
            self.encoded = variable_encode(decoded)
            self.valid = False

            return False

        # Go!
        self.to_python(decoded)

        if self.submitted and self.valid and self.persistent:
            # Store params to session
            # Restrict to form data
            session[self.session_key] = {
                k: str(v)
                for k, v in self.encoded.items()
                if k not in self.volatile_items and not k.endswith('--repetitions') and v is not None
            }

        return self.valid

    def value(self, name):
        """
        Get form value for input from name
        Returned value is coerced to string for rendering purpose.

        @param string name, name of the input to get value for
        """

        if not name:
            return ''

        data = self.decoded
        for part in name.split('.'):
            index = None
            if '-' in part:
                part, index = part.split('-')
                index = int(index)

            if part not in data:
                return ''

            data = data.get(part)
            if index is not None:
                if index >= len(data):
                    return ''
                data = data[index]

        # Coerce data to string
        def coerce_str(data):
            if data is None:
                return ''

            if isinstance(data, (list, tuple)):
                return list(map(coerce_str, data))

            if isinstance(data, dict):
                return {
                    k: coerce_str(v)
                    for k, v in data.items()
                }

            return str(data)

        return coerce_str(data)

    def set_data(self, value, validate=False):
        """
        Convert `value` from its Python representation to the foreign
        representation using formencode validator (deprecated)
        """

        warnings.warn('`Form.set_data()` is deprecated and will be removed soon; use `Form.from_python()`', DeprecationWarning, stacklevel=2)
        return self.from_python(value, validate=validate)


class State:
    """ Form state object """

    def __init__(self, request):
        self.request = request

    def pluralize(self, singular, plural, num, **kwargs):
        """ Wrapper to request.pluralize() """

        translated = self.request.pluralize(singular, plural, num, **kwargs)
        if translated in (singular, plural):
            # Translation failed, try the FormEncode domain
            kwargs['domain'] = 'FormEncode'
            translated = self.request.pluralize(singular, plural, num, **kwargs)

        return translated

    def translate(self, tstring, **kwargs):
        """ Wrapper to request.translate() """

        translated = self.request.translate(tstring, **kwargs)
        if translated == tstring:
            # Translation failed, try the FormEncode domain
            kwargs['domain'] = 'FormEncode'
            translated = self.request.translate(tstring, **kwargs)

        return translated

    # Formencode needs this to translate error messages
    _ = translate


def on_before_renderer(event):
    """ Add forms and form_ctx dictionaries to renderer context """
    request = event['request']
    event['forms'] = request.forms
    event['form_ctx'] = request.form_ctx


def on_new_request(event):
    """
    Add forms and form_ctx dictionaries to request

    forms dictionary will carry all forms object using form's name as key
    form_ctx dictionary will carry current form context:
        'current' key is reserved for current form object
        'select_options' key is reserved when building select html tag
    """
    request = event.request
    request.forms = {}
    request.form_ctx = {}


def validate(name, schema, **form_kwargs):
    """
    Form validation decorator

    Data is validated with a FormEncode schema
    """

    def wrapper(func, *args, **kwargs):
        """ Decorator Wrapper function """

        # Get request object from args
        # First arg is «self» when func is a method
        request = get_instance_from_args(args)

        # Initialize form object
        state = State(request)
        form = Form(name, schema, state, **form_kwargs)

        # Validate the form
        form.validate()

        # Store the form
        request.forms[name] = form

        return func(*args, **kwargs)

    return decorator(wrapper)


def includeme(config):
    """
    Set up standard configurator registrations. Use via:

    .. code-block:: python

    config = Configurator()
    config.include('pyramid_helpers.forms')
    """

    config.add_subscriber(on_before_renderer, 'pyramid.events.BeforeRender')
    config.add_subscriber(on_new_request, 'pyramid.events.NewRequest')
