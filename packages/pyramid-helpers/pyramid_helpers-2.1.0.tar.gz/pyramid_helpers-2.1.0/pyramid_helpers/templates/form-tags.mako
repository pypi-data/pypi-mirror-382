<%!
import json

from markupsafe import escape
from pyramid.settings import asbool


def coerce_bool(value):
    """ Coerce pseudo boolean to boolean """

    if isinstance(value, str):
        return asbool(value)

    if isinstance(value, bool):
        return value

    raise TypeError('{0!r} could not be coerced to boolean'.format(value))


def render_attrs(attrs, xhtml=False):
    """ Render HTML attributes """

    html = []

    for key, value in attrs.items():
        key = key.replace('_', '-')

        if key.endswith('-'):
            key = key[:-1]

        if key in ('autofocus', 'checked', 'disabled', 'multiple', 'readonly', 'required', 'selected') and not isinstance(value, bool):
            value = str(value).lower()
            value = asbool(value) or value == key

        if isinstance(value, bool):
            if value:
                html.append(f'{key}="{key}"' if xhtml else key)
        else:
            html.append(f'{key}="{escape(str(value))}"')

    if not html:
        return ''

    return ' '.join(html)


def render_tag(tag, content='', xhtml=False, **attrs):
    """ Render an HTML tag """

    html_attrs = render_attrs(attrs, xhtml=xhtml)
    if html_attrs:
        html_attrs = f' {html_attrs}'

    close1 = ' />' if xhtml and not content else '>'
    close2 = f'</{tag}>' if content or tag != 'input' else ''

    return f'<{tag}{html_attrs}{close1}{content}{close2}'
%>\
<%doc>

    Mako form tag library.

    Implement HTML form tags into <%defs> which are readily usable via <%call>.

    The <%call> tags themselves can be more pleasantly used in templates using a
    preprocessor such as process_tags(), which converts XML-style tags into <%call> tags.

</%doc>

<%def name="autocomplete(name, **attrs)">\
<%doc>
    Render an HTML <select> tag.  Options within the tag
    are generated from selected value(s).
</%doc>
<%
    value = form_ctx['current'].value(name) or []
    if isinstance(value, str):
        value = [value]

    attrs['data-value'] = json.dumps(value)
%>\
${render_tag('select', name=name, **attrs) | n}\
${errors(name)}\
</%def>

<%def name="checkbox(name, value='true', **attrs)">\
<%doc>
    Render an HTML <checkbox> tag.  The value is rendered as 'true'
    by default for usage with the StringBool validator.
</%doc>
<%
    data = form_ctx['current'].value(name)
    if isinstance(data, (list, tuple)):
        checked = str(value) in data
    else:
        checked = str(value) == data
%>\
${render_tag('input', name=name, checked=checked, type_='checkbox', value=value, **attrs) | n}\
${errors(name)}
</%def>

<%def name="color(name, **attrs)">\
<%doc>
    Render an HTML <input type="color"> tag.
</%doc>
${render_tag('input', name=name, type_='color', value=form_ctx['current'].value(name), **attrs) | n}\
${errors(name)}\
</%def>

<%def name="date(name, **attrs)">\
<%doc>
    Render an HTML <input type="date"> tag.
</%doc>
${render_tag('input', name=name, type_='date', value=form_ctx['current'].value(name), **attrs) | n}\
${errors(name)}\
</%def>

<%def name="datetime_local(name, **attrs)">\
<%doc>
    Render an HTML <input type="datetime-local"> tag.
</%doc>
${render_tag('input', name=name, type_='datetime-local', value=form_ctx['current'].value(name), **attrs) | n}\
${errors(name)}\
</%def>

<%def name="email(name, **attrs)">\
<%doc>
    Render an HTML <input type="email"> tag.
</%doc>
${render_tag('input', name=name, type_='email', value=form_ctx['current'].value(name), **attrs) | n}\
${errors(name)}\
</%def>

<%def name="errors(name, extra_class=None)">\
<%doc>
    Given a field name, produce a stylized error message from the current
    form errors collection, if one is present.  Else render nothing.
</%doc>
<% error = form_ctx['current'].error(name) %>\
% if error:
<div class="alert alert-danger mt-2 form-error${' {0}'.format(extra_class) if extra_class else ''}" role="alert">
    ${error}
</div>
% endif
</%def>

<%def name="form(name, action=None, multipart=False, **attrs)">
<%doc>
    Render an HTML <form> tag - the body contents will be rendered within.

        name - the name of the form stored in request attribute
        action - url to be POSTed to
</%doc>
<%
    # Get form instance
    if name not in forms:
        raise ValueError(f'Invalid form name {name}')

    form_ctx['current'] = forms[name]

    content = []

    if form_ctx['current'].csrf_token:
        content.append(render_tag('input', name='_csrf_token', type_='hidden', value=form_ctx['current'].csrf_token))

    content.append(capture(caller.body).strip())
%>\
${render_tag('form', action=action or request.path_qs, content='\n'.join(content), multipart=coerce_bool(multipart), name=name, **attrs) | n}\
<% del form_ctx['current'] %>\
</%def>

<%def name="hidden(name, **attrs)">\
<%doc>
    Render an HTML <input type="hidden"> tag.
</%doc>
${render_tag('input', name=name, type_='hidden', value=form_ctx['current'].value(name), **attrs) | n}\
${errors(name)}\
</%def>\

<%def name="month(name, **attrs)">\
<%doc>
    Render an HTML <input type="month"> tag.
</%doc>
${render_tag('input', name=name, type_='month', value=form_ctx['current'].value(name), **attrs) | n}\
${errors(name)}\
</%def>

<%def name="number(name, **attrs)">\
<%doc>
    Render an HTML <input type="number"> tag.
</%doc>
${render_tag('input', name=name, type_='number', value=form_ctx['current'].value(name), **attrs) | n}\
${errors(name)}\
</%def>

<%def name="optgroup(label, **attrs)">\
<%doc>
    Render an HTML <optgroup> tag.  This is meant to be used with
    the "select" %def and produces a special return value specific to
    usage with that function.
</%doc>
${render_tag('optgroup', content=capture(caller.body).strip(), label=label, **attrs) | n}\
</%def>

<%def name="option(value)">\
<%doc>
    Render an HTML <option> tag.  This is meant to be used with
    the "select" %def and produces a special return value specific to
    usage with that function.
</%doc>
<% selected = str(value) in form_ctx['select_value'] %>\
${render_tag('option', content=capture(caller.body).strip(), selected=selected, value=value) | n}\
</%def>

<%def name="password(name, **attrs)">\
<%doc>
    Render an HTML <input type="password"> tag.
</%doc>
${render_tag('input', name=name, type_='password', value=form_ctx['current'].value(name), **attrs) | n}\
${errors(name)}\
</%def>

<%def name="radio(name, value='true', **attrs)">\
<%doc>
    Render an HTML <radio> tag.
</%doc>
<%
    data = form_ctx['current'].value(name)
    if isinstance(data, (list, tuple)):
        checked = str(value) in data
    else:
        checked = str(value) == data
%>\
${render_tag('input', name=name, checked=checked, type_='radio', value=value, **attrs) | n}\
${errors(name)}\
</%def>

<%def name="range(name, **attrs)">\
<%doc>
    Render an HTML <input type="range"> tag.
</%doc>
${render_tag('input', name=name, type_='range', value=form_ctx['current'].value(name), **attrs) | n}\
${errors(name)}\
</%def>

<%def name="search(name, **attrs)">\
<%doc>
    Render an HTML <input type="search"> tag.
</%doc>
${render_tag('input', name=name, type_='search', value=form_ctx['current'].value(name), **attrs) | n}\
${errors(name)}\
</%def>

<%def name="select(name, **attrs)">\
<%doc>
    Render an HTML <select> tag.  Options within the tag
    are generated using the "option" %def.
</%doc>
<%
    value = form_ctx['current'].value(name) or []
    if isinstance(value, str):
        value = [value]

    form_ctx['select_value'] = list(map(str, value))
%>\
${render_tag('select', content=capture(caller.body).strip(), name=name, **attrs) | n}\
${errors(name)}\
<% del form_ctx['select_value'] %>\
</%def>

<%def name="tel(name, **attrs)">\
<%doc>
    Render an HTML <input type="tel"> tag.
</%doc>
${render_tag('input', name=name, type_='tel', value=form_ctx['current'].value(name), **attrs) | n}\
${errors(name)}\
</%def>

<%def name="text(name, **attrs)">\
<%doc>
    Render an HTML <input type="text"> tag.
</%doc>
${render_tag('input', name=name, type_='text', value=form_ctx['current'].value(name), **attrs) | n}\
${errors(name)}\
</%def>

<%def name="textarea(name, **attrs)">\
<%doc>
    Render an HTML <textarea></textarea> tag pair with embedded content.
</%doc>
${render_tag('textarea', name=name, content=form_ctx['current'].value(name), **attrs) | n}\
${errors(name)}\
</%def>

<%def name="time(name, **attrs)">\
<%doc>
    Render an HTML <input type="time"> tag.
</%doc>
${render_tag('input', name=name, type_='time', value=form_ctx['current'].value(name), **attrs) | n}\
${errors(name)}\
</%def>

<%def name="upload(name, **attrs)">\
<%doc>
    Render an HTML <file> tag.
</%doc>
${render_tag('input', name=name, type_='file', **attrs) | n}\
${errors(name)}\
</%def>

<%def name="url(name, **attrs)">\
<%doc>
    Render an HTML <input type="url"> tag.
</%doc>
${render_tag('input', name=name, type_='url', value=form_ctx['current'].value(name), **attrs) | n}\
${errors(name)}\
</%def>

<%def name="week(name, **attrs)">\
<%doc>
    Render an HTML <input type="week"> tag.
</%doc>
${render_tag('input', name=name, type_='week', value=form_ctx['current'].value(name), **attrs) | n}\
${errors(name)}\
</%def>
