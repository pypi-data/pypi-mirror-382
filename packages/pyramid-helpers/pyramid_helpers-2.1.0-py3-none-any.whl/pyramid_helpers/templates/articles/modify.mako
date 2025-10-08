<%namespace file="/form-tags.mako" name="form"/>\
<%inherit file="/site.mako" />\
<%form:form name="article" method="post">
<div class="card">
    <div class="card-header">
        <h2 class="card-title h5 pt-2">${title}</h2>
    </div>

    <div class="card-body">
        <div class="mb-3">
            <label class="form-label" for="title">${translate('Title')}</label>
            <%form:text id="title" name="title" class_="form-control" />
        </div>

        <div class="mb-3">
            <label class="form-label" for="status">${translate('Status')}</label>
            <%form:select id="status" name="status" class_="form-control form-select">
                <%form:option value=""></%form:option>
                <%form:option value="draft">${translate('Draft')}</%form:option>
                <%form:option value="published">${translate('Published')}</%form:option>
                <%form:option value="refused">${translate('Refused')}</%form:option>
            </%form:select>
        </div>

        <div class="mb-3">
            <label class="form-label" for="text">${translate('Text')}</label>
            <%form:textarea id="text" name="text" rows="10" cols="50" class_="form-control"/>
        </div>
    </div><!-- /.card-body -->

    <div class="card-footer text-end">
        <a class="btn btn-secondary me-3" href="${cancel_link}" title="${translate('Cancel')}">${translate('Cancel')}</a>
        <input class="btn btn-primary" type="submit" name="save" value="${translate('Save')}" />
    </div><!-- /.card-footer -->
</div><!-- /.card -->
</%form:form>
