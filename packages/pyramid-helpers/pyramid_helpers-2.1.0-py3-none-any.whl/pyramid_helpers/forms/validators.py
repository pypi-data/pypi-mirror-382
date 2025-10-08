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

""" Form validators for Pyramid """


import datetime
import re

import formencode
from formencode import validators
from formencode.compound import from_python
from formencode.national import InternationalPhoneNumber

from pyramid_helpers.i18n import N_


COLOR_RE = re.compile(r'#(?P<r>[0-9a-f]{2})(?P<v>[0-9a-f]{2})(?P<b>[0-9a-f]{2})', re.I)
MONTH_RE = re.compile(r'(?P<year>\d{4})-(?P<month>\d{2})')
TIME_RE = re.compile(r'(?P<hours>\d{2}):(?P<minutes>\d{2})')
WEEK_RE = re.compile(r'(?P<year>\d{4})-W(?P<week>\d{2})')


#
# Validators
#
class Color(formencode.FancyValidator):
    """ Formencode validator for color representation (#RRVVBB) """

    messages = {
        'invalid': N_('Invalid value'),
    }

    format = 'hex'

    # pylint: disable=unused-argument
    def _convert_from_python(self, value, state):
        if isinstance(value, (list, tuple)):
            value = f'#{value[0]:02x}{value[1]:02x}{value[2]:02x}'

        return value

    def _convert_to_python(self, value, state):
        match = COLOR_RE.match(value)
        if match is None:
            raise formencode.Invalid(self.message('invalid', state), value, state)

        if self.format == 'hex':
            return value

        return [int(v, 16) for v in match.groups()]


class DateTime(validators.FancyValidator):
    """ Formencode validator for datetime representation using given format """

    messages = {
        'invalid': N_('Invalid value'),
        'year': N_('Year must be >= 1900'),
    }

    format = N_('%m/%d/%Y')
    is_date = False
    is_local = True
    is_localized = True

    def _convert_from_python(self, value, state):
        if not isinstance(value, (datetime.datetime, datetime.date)):
            raise formencode.Invalid(self.message('invalid', state), value, state)

        format_ = state.translate(self.format) if self.is_localized else self.format

        # strftime requires year to be >= 1900
        if value.year < 1900:
            raise formencode.Invalid(self.message('year', state), value, state)

        return value.strftime(format_)

    def _convert_to_python(self, value, state):
        if isinstance(value, (datetime.datetime, datetime.date)):
            return value

        format_ = state.translate(self.format) if self.is_localized else self.format
        try:
            date = datetime.datetime.strptime(value, format_)
            if self.is_date:
                date = date.date()
            elif self.is_local:
                # Add local timezone
                date = state.request.localize(date)
            else:
                # Add UTC timezone
                date = date.replace(tzinfo=datetime.timezone.utc)
        except ValueError as exc:
            raise formencode.Invalid(self.message('invalid', state), value, state) from exc

        # strftime used in _convert_from_python requires year to be >= 1900
        if date.year < 1900:
            raise formencode.Invalid(self.message('year', state), value, state)

        return date


class List(formencode.ForEach):
    """
    Modified version of formencode.ForEach which uses csv format in a single
    field instead of repeating the field.
    """

    messages = {
        'invalid': N_('Invalid value'),
    }

    format = '{}'
    if_empty = []
    if_missing = []
    separator = ','
    strip = True

    # pylint: disable=comparison-with-callable
    def _attempt_convert(self, value, state, validate):
        if validate == from_python:
            # Calling inherited
            value = super()._attempt_convert(value, state, validate)

            try:
                value = self.separator.join(self.format.format(v) for v in value)
            except Exception as exc:
                raise formencode.Invalid(self.message('invalid', state), value, state) from exc
        else:
            # to_python
            try:
                value = value.split(self.separator)

                if self.strip:
                    value = [v.strip() for v in value]

            except Exception as exc:
                raise formencode.Invalid(self.message('invalid', state), value, state) from exc

            # Calling inherited
            value = super()._attempt_convert(value, state, validate)

        return value

    def empty_value(self, value):
        return ''


class Month(formencode.FancyValidator):
    """ Formencode validator for month representation (YYYY-MM) """

    messages = {
        'invalid': N_('Invalid value'),
        'month-min': N_('Month must be >= 1'),
        'month-max': N_('Month must be <= 12'),
        'year-min': N_('Year must be >= 1900')
    }

    # pylint: disable=unused-argument
    def _convert_from_python(self, value, state):
        if isinstance(value, (list, tuple)):
            value = f'{value[0]:04d}-{value[1]:02d}'

        return value

    def _convert_to_python(self, value, state):
        match = MONTH_RE.match(value)
        if match is None:
            raise formencode.Invalid(self.message('invalid', state), value, state)

        year, month = list(map(int, match.groups()))

        if year < 1900:
            raise formencode.Invalid(self.message('year-min', state), value, state)

        if month < 1:
            raise formencode.Invalid(self.message('month-min', state), value, state)

        if month > 12:
            raise formencode.Invalid(self.message('month-max', state), value, state)

        return (year, month)


class Time(formencode.FancyValidator):
    """ Formencode validator for time representation (hh:mm) """

    messages = {
        'invalid': N_('Invalid value'),
        'hours-min': N_('Hours must be >= 00'),
        'hours-max': N_('Hours must be <= 23'),
        'minutes-min': N_('Minutes must be >= 00'),
        'minutes-max': N_('Minutes must be <= 59'),
    }

    # pylint: disable=unused-argument
    def _convert_from_python(self, value, state):
        if isinstance(value, (list, tuple)):
            value = f'{value[0]:02d}:{value[1]:02d}'

        return value

    def _convert_to_python(self, value, state):
        match = TIME_RE.match(value)
        if match is None:
            raise formencode.Invalid(self.message('invalid', state), value, state)

        hours, minutes = list(map(int, match.groups()))

        if hours < 0:
            raise formencode.Invalid(self.message('hours-min', state), value, state)

        if hours > 23:
            raise formencode.Invalid(self.message('hours-max', state), value, state)

        if minutes < 0:
            raise formencode.Invalid(self.message('minutes-min', state), value, state)

        if minutes > 59:
            raise formencode.Invalid(self.message('minutes-max', state), value, state)

        return (hours, minutes)


class Week(formencode.FancyValidator):
    """ Formencode validator for week representation (YYYY-WXX) """

    messages = {
        'invalid': N_('Invalid value'),
        'week-min': N_('Week must be >= 1'),
        'week-max': N_('Week must be <= 52'),
        'year-min': N_('Year must be >= 1900'),
    }

    # pylint: disable=unused-argument
    def _convert_from_python(self, value, state):
        if isinstance(value, (list, tuple)):
            value = f'{value[0]:04d}-W{value[1]:02d}'

        return value

    def _convert_to_python(self, value, state):
        match = WEEK_RE.match(value)
        if match is None:
            raise formencode.Invalid(self.message('invalid', state), value, state)

        year, week = list(map(int, match.groups()))

        if year < 1900:
            raise formencode.Invalid(self.message('year-min', state), value, state)

        if week < 1:
            raise formencode.Invalid(self.message('week-min', state), value, state)

        if week > 52:
            raise formencode.Invalid(self.message('week-max', state), value, state)

        return (year, week)


#
# Test Form
#
class ValidatorsForm(formencode.Schema):
    """ Pyramid-Helpers test form """

    allow_extra_fields = True
    filter_extra_fields = True

    checkbox_input = validators.StringBool(if_missing=False, if_empty=False)
    color_input = Color(format='rvb', if_missing=None, if_empty=None)
    date_input = DateTime(format='%Y-%m-%d', if_missing=None, if_empty=None, is_date=True, is_localized=False)
    datetime_loc_input = DateTime(format='%Y-%m-%dT%H:%M', if_missing=None, if_empty=None, is_localized=False, is_local=True)
    datetime_utc_input = DateTime(format='%Y-%m-%dT%H:%M', if_missing=None, if_empty=None, is_localized=False, is_local=False)
    email_input = validators.Email(if_missing=None, if_empty=None)
    list_input = List()
    month_input = Month(if_missing=None, if_empty=None)
    number_input = validators.Number(if_missing=None, if_empty=None)
    password_input = validators.String(if_missing=None, if_empty=None)
    radio_input = validators.OneOf(['one', 'two', 'three'], if_missing=None, if_empty=None)
    range_input = validators.Int(min=0, max=100, if_missing=None, if_empty=None)
    search_input = validators.String(if_missing=None, if_empty=None)
    select_input1 = validators.OneOf(['one', 'two', 'three'], if_missing=None, if_empty=None)
    select_input2 = validators.OneOf(['banana', 'orange', 'apple'], if_missing=None, if_empty=None)
    tel_input = InternationalPhoneNumber(if_missing=None, if_empty=None)
    text_input = validators.String(if_missing=None, if_empty=None)
    textarea_input = validators.String(if_missing=None, if_empty=None)
    time_input = Time(if_missing=None, if_empty=None)
    upload_input = validators.FieldStorageUploadConverter(if_missing=None, if_empty=None)
    url_input = validators.URL(if_missing=None, if_empty=None)
    week_input = Week(if_missing=None, if_empty=None)
