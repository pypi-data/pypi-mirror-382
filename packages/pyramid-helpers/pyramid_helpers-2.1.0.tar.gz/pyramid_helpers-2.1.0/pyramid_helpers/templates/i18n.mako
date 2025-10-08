<%!
import datetime

from pyramid_helpers.utils import get_tzinfo
%>\
<%inherit file="/site.mako" />\
<h2>${translate('I18n')}</h2>

<%
tzinfo = get_tzinfo(request)
date = datetime.datetime(2021, 1, 1)
date_utc = datetime.datetime(2021, 1, 1, tzinfo=datetime.timezone.utc)
date_loc = datetime.datetime(2021, 1, 1, tzinfo=tzinfo)
%>\
<b>Aware datetime</b> (UTC)
<pre class="bg-light border rounded p-3">
date_utc = datetime.datetime(2021, 1, 1, tzinfo=datetime.timezone.utc)          # ${date_utc}

format_date(date_utc)                                                           # ${format_date(date_utc)}
format_datetime(date_utc)                                                       # ${format_datetime(date_utc)}
format_date(date_utc, format='long')                                            # ${format_date(date_utc, format='long')}
format_datetime(date_utc, date_format='long')                                   # ${format_datetime(date_utc, date_format='long')}
format_datetime(date_utc, date_format='short')                                  # ${format_datetime(date_utc, date_format='short')}
format_datetime(date_utc, date_format='short', time_format='short')             # ${format_datetime(date_utc, date_format='short', time_format='short')}
format_datetime(localize(date_utc), date_format='short', time_format='short')   # ${format_datetime(localize(date_utc), date_format='short', time_format='short')}
format_datetime(localtoutc(date_utc), date_format='short', time_format='short') # ${format_datetime(localtoutc(date_utc), date_format='short', time_format='short')}
format_datetime(utctolocal(date_utc), date_format='short', time_format='short') # ${format_datetime(utctolocal(date_utc), date_format='short', time_format='short')}
format_time(date_utc)                                                           # ${format_time(date_utc)}
format_time(date_utc, format='short')                                           # ${format_time(date_utc, format='short')}
</pre>

<b>Aware datetime</b> (${tzinfo})
<pre class="bg-light border rounded p-3">
get_tzinfo(request)                                                             # ${tzinfo}
date_loc = datetime.datetime(2021, 1, 1, tzinfo=get_tzinfo(request))            # ${date_loc}

format_date(date_loc)                                                           # ${format_date(date_loc)}
format_datetime(date_loc)                                                       # ${format_datetime(date_loc)}
format_date(date_loc, format='long')                                            # ${format_date(date_loc, format='long')}
format_datetime(date_loc, date_format='long')                                   # ${format_datetime(date_loc, date_format='long')}
format_datetime(date_loc, date_format='short')                                  # ${format_datetime(date_loc, date_format='short')}
format_datetime(date_loc, date_format='short', time_format='short')             # ${format_datetime(date_loc, date_format='short', time_format='short')}
format_datetime(localize(date_loc), date_format='short', time_format='short')   # ${format_datetime(localize(date_loc), date_format='short', time_format='short')}
format_datetime(localtoutc(date_loc), date_format='short', time_format='short') # ${format_datetime(localtoutc(date_loc), date_format='short', time_format='short')}
format_datetime(utctolocal(date_loc), date_format='short', time_format='short') # ${format_datetime(utctolocal(date_loc), date_format='short', time_format='short')}
format_time(date_loc)                                                           # ${format_time(date_loc)}
format_time(date_loc, format='short')                                           # ${format_time(date_loc, format='short')}
</pre>

<b>Naive datetime</b> (deprecated)
<pre class="bg-light border rounded p-3">
date = datetime.datetime(2021, 1, 1)                                            # ${date}

format_date(date)                                                               # ${format_date(date)}
format_datetime(date)                                                           # ${format_datetime(date)}
format_date(date, format='long')                                                # ${format_date(date, format='long')}
format_datetime(date, date_format='long')                                       # ${format_datetime(date, date_format='long')}
format_datetime(date, date_format='short')                                      # ${format_datetime(date, date_format='short')}
format_datetime(date, date_format='short', time_format='short')                 # ${format_datetime(date, date_format='short', time_format='short')}
format_datetime(localize(date), date_format='short', time_format='short')       # ${format_datetime(localize(date), date_format='short', time_format='short')}
format_datetime(localtoutc(date), date_format='short', time_format='short')     # ${format_datetime(localtoutc(date), date_format='short', time_format='short')}
format_datetime(utctolocal(date), date_format='short', time_format='short')     # ${format_datetime(utctolocal(date), date_format='short', time_format='short')}
format_time(date)                                                               # ${format_time(date)}
format_time(date, format='short')                                               # ${format_time(date, format='short')}
</pre>

<b>Number</b>
<pre class="bg-light border rounded p-3">
format_decimal(1.01)                                                            # ${format_decimal(1.01)}
</pre>

<b>Translation and plural</b> (${request.locale_name})
<pre class="bg-light border rounded p-3">
translate('Title')                                                              # ${translate('Title')}

% for num in range(4):
pluralize('{0} article', '{0} articles', ${num}).format(${num})                           # ${pluralize('{0} article', '{0} articles', num).format(num)}
% endfor
</pre>
