<%!
import pprint
%>\
<%namespace name="form" file="/form-tags.mako"/>\
<%inherit file="/site.mako" />\
<%def name="head()">
${parent.head()}\
    <!-- Easypick -->
    <script src="//cdn.jsdelivr.net/npm/@easepick/bundle@1.2.0/dist/index.umd.min.js"></script>

    <!-- Inputmask -->
    <script src="//cdn.jsdelivr.net/npm/inputmask@5.0.7/dist/inputmask.min.js"></script>
</%def>\
<%def name="foot()">
${parent.foot()}\
<script>
// Week
Inputmask('9999-W99').mask('#week-input');

// Month
Inputmask('9999-99').mask('#month-input');

// Date
new easepick.create({
    element: '#date-input',
    css: [
        "//cdn.jsdelivr.net/npm/@easepick/bundle@1.2.0/dist/index.css"
    ],
    zIndex: 10,
    lang: "${localizer.locale_name}",
    format: 'YYYY-MM-DD'
});

// Datetime (LOC)
new easepick.create({
    element: '#datetime-loc-input',
    css: [
        "//cdn.jsdelivr.net/npm/@easepick/bundle@1.2.0/dist/index.css"
    ],
    zIndex: 10,
    lang: "${localizer.locale_name}",
    format: 'YYYY-MM-DDTHH:mm',
    plugins: [
        "TimePlugin"
    ]
});

// Datetime (UTC)
new easepick.create({
    element: '#datetime-utc-input',
    css: [
        "//cdn.jsdelivr.net/npm/@easepick/bundle@1.2.0/dist/index.css"
    ],
    zIndex: 10,
    lang: "${localizer.locale_name}",
    format: 'YYYY-MM-DDTHH:mm',
    plugins: [
        "TimePlugin"
    ]
});
</script>
</%def>\

<h2>${translate('Validators')}</h2>
<%form:form name="validators_form" method="post" enctype="multipart/form-data">
    <%form:hidden name="hidden_input" />
    <fieldset class="border rounded mb-5">
        <legend class="bg-light border-bottom px-3 py-2">${translate('Standard inputs')}</legend>

        <div class="p-3">
            <label class="form-label" for="text-input">${translate('Text')}</label>
            <%form:text id="text-input" name="text_input" class_="form-control" />
        </div>

        <div class="p-3">
            <label class="form-label" for="textarea-input">${translate('Text area')}</label>
            <%form:textarea id="textarea-input" name="textarea_input" class_="form-control"></%form:textarea>
        </div>

        <div class="p-3">
            <label class="form-label" for="password-input">${translate('Password')}</label>
            <%form:password id="password-input" name="password_input" class_="form-control" />
        </div>

        <div class="p-3">
            <label class="form-label" for="search-input">${translate('Search')}</label>
            <%form:search id="search-input" name="search_input" class_="form-control" />
        </div>

        <div class="p-3">
            <label>
                <%form:checkbox id="checkbox-input" name="checkbox_input" value="true" />
                ${translate('Checkbox')}
            </label>
        </div>

        <div class="p-3">
            <label>
                <%form:radio id="radio-input-1" name="radio_input" value="one" />
                ${translate('Radio (One)')}
            </label>
            <label>
                <%form:radio id="radio-input-2" name="radio_input" value="two" />
                ${translate('Radio (Two)')}
            </label>
            <label>
                <%form:radio id="radio-input-3" name="radio_input" value="three" />
                ${translate('Radio (Three)')}
            </label>
            <label>
                <%form:radio id="radio-input-4" name="radio_input" value="invalid" />
                ${translate('Radio (Invalid)')}
            </label>
        </div>

        <div class="p-3">
            <label class="form-label" for="select-input1">${translate('Select (Numbers)')}</label>
            <%form:select id="select-input1" name="select_input1" class_="form-control form-select">
                <%form:option value="">--</%form:option>
                <%form:option value="one">${translate('One')}</%form:option>
                <%form:option value="two">${translate('Two')}</%form:option>
                <%form:option value="three">${translate('Three')}</%form:option>
                <%form:option value="invalid">${translate('Invalid')}</%form:option>
            </%form:select>
        </div>

        <div class="p-3">
            <label class="form-label" for="select-input2">${translate('Select (Fruits)')}</label>
            <%form:select id="select-input2" name="select_input2" class_="form-control form-select">
                <%form:option value="">--</%form:option>
                <%form:optgroup label="${translate('Fruits')}">
                    <%form:option value="apple">${translate('Apple')}</%form:option>
                    <%form:option value="banana">${translate('Banana')}</%form:option>
                    <%form:option value="orange">${translate('Orange')}</%form:option>
                </%form:optgroup>
                <%form:optgroup label="${translate('Numbers')}">
                    <%form:option value="one">${translate('One')}</%form:option>
                    <%form:option value="two">${translate('Two')}</%form:option>
                    <%form:option value="three">${translate('Three')}</%form:option>
                </%form:optgroup>
            </%form:select>
        </div>

        <div class="p-3">
            <label class="form-label" for="upload-input">${translate('Upload')}</label>
            <%form:upload id="upload-input" name="upload_input" />
        </div>
    </fieldset>

    <fieldset class="border rounded mb-5">
        <legend class="bg-light border-bottom px-3 py-2">${translate('Number inputs')}</legend>

        <div class="p-3">
            <label class="form-label" for="number-input">${translate('Number')}</label>
            <%form:number id="number-input" name="number_input" class_="form-control" />
        </div>

        <div class="p-3">
            <label class="form-label" for="range-input">${translate('Range')} (0-100)</label>
            <%form:range id="range-input" name="range_input" class_="form-control" />
        </div>
    </fieldset>

    <fieldset class="border rounded mb-5">
        <legend class="bg-light border-bottom px-3 py-2">${translate('Communication inputs')}</legend>

        <div class="p-3">
            <label class="form-label" for="url-input">${translate('Url')}</label>
            <%form:url id="url-input" name="url_input" class_="form-control" />
        </div>

        <div class="p-3">
            <label class="form-label" for="email-input">${translate('Email')}</label>
            <%form:email id="email-input" name="email_input" class_="form-control" />
        </div>

        <div class="p-3">
            <label class="form-label" for="tel-input">${translate('Tel')}</label>
            <%form:tel id="tel-input" name="tel_input" class_="form-control" />
        </div>
    </fieldset>

    <fieldset class="border rounded mb-5">
        <legend class="bg-light border-bottom px-3 py-2">${translate('Date/time inputs')}</legend>

        <div class="p-3">
            <label class="form-label" for="time-input">${translate('Time')}</label>
            <%form:time id="time-input" name="time_input" class_="form-control" placeholder="HH:mm"/>
        </div>

        <div class="p-3">
            <label class="form-label" for="week-input">${translate('Week')}</label>
            <%form:week id="week-input" name="week_input" class_="form-control" placeholder="YYYY-WNN"/>
        </div>

        <div class="p-3">
            <label class="form-label" for="month-input">${translate('Month')}</label>
            <%form:month id="month-input" name="month_input" class_="form-control" placeholder="YYYY-MM" />
        </div>

        <div class="p-3">
            <label class="form-label" for="date-input">${translate('Date')}</label>
            <%form:date id="date-input" name="date_input" class_="form-control" />
        </div>

        <div class="p-3">
            <label class="form-label" for="datetime-loc-input">${translate('Datetime (LOC)')}</label>
            <%form:datetime_local id="datetime-loc-input" name="datetime_loc_input" class_="form-control" placeholder="YYYY-MM-DDTHH:mm"/>
        </div>

        <div class="p-3">
            <label class="form-label" for="datetime-utc-input">${translate('Datetime (UTC)')}</label>
            <%form:datetime_local id="datetime-utc-input" name="datetime_utc_input" class_="form-control" placeholder="YYYY-MM-DDTHH:MM"/>
        </div>
    </fieldset>

    <fieldset class="border rounded mb-2">
        <legend class="bg-light border-bottom px-3 py-2">${translate('Miscellaneous inputs')}</legend>

        <div class="p-3">
            <label class="form-label" for="color-input">${translate('Color')}</label>
            <%form:color id="color-input" name="color_input" class_="form-control" />
        </div>

        <div class="p-3">
            <label class="form-label" for="list-input">${translate('List')}</label>
            <%form:text id="list-input" name="list_input" class_="form-control" placeholder="item1,item2,item3"/>
        </div>
    </fieldset>

    <div class="p-3 text-end">
        <input class="btn btn-primary" type="submit" name="submit_input" value="${translate('Submit')}" />
    </div>
</%form:form>

% if errors:
<h3>${translate('Errors')}</h3>
<pre class="bg-danger border border-danger rounded p-3" style="--bs-bg-opacity: .2;">${pprint.pformat(errors)}</pre>
% elif result:
<h3>${translate('Result')}</h3>
<pre class="bg-success border border-success rounded p-3" style="--bs-bg-opacity: .2;">${pprint.pformat(result)}</pre>
% endif
