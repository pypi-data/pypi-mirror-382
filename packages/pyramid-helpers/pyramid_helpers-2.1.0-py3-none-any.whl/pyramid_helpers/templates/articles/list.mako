<%namespace file="/paginate.mako" name="paginate"/>\
<%
labels = {
    'draft': 'warning',
    'published': 'success',
    'refused': 'danger',
}
pager = request.pagers['articles']
%>\
% if pager.total:
<div class="d-flex mb-3">
    <div class="flex-grow-1">
    % if pager.pages > 1:
        ${translate('article from {0} to {1} on {2}').format(pager.first_item, pager.last_item, pager.total)}
    % else:
        ${pluralize('{0} article', '{0} articles', pager.total).format(pager.total)}
    % endif
    </div>
    <div>
        <% _query = {'csv': 1} %>\
        <a class="btn btn-outline-secondary btn-sm" href="${request.route_path('articles.search', _query=_query)}" title="${translate('Download CSV')}">
            <i class="fa fa-download fa-fw me-1"></i>
            CSV
        </a>
    </div>
</div>

<table class="table table-bordered">
    <tbody>
    % for article in pager:
        <tr>
            <td>
                <a class="text-decoration-none" href="${request.route_path('articles.visual', article=article.id)}" title="${translate('View article "{0}"').format(article.title)}">#${article.id}</a>
            </td>
            <td>
                <a class="text-decoration-none" href="${request.route_path('articles.visual', article=article.id)}" title="${translate('View article "{0}"').format(article.title)}">${article.title}</a>
            </td>
            <td>
                ${translate(article.status.capitalize())}
            </td>
        % if has_permission('articles.modify'):
            <td class="text-end">
            % if has_permission('articles.delete'):
                <a class="btn btn-outline-danger btn-sm" href="${request.route_path('articles.delete', article=article.id)}" title="${translate('Delete article {0}').format(article.title)}"><i class="fa fa-trash-alt fa-fw"></i><span class="sr-only">${translate('delete')}</span></a>
            % endif>
                <a class="btn btn-outline-primary btn-sm me-2" href="${request.route_path('articles.modify', article=article.id)}" title="${translate('Edit article {0}').format(article.title)}"><i class="fa fa-edit fa-fw"></i><span class="sr-only">${translate('modify')}</span></a>
            </td>
        % endif
        </tr>
    % endfor
    </tbody>
    <thead>
        <th>
            <a class="partial-link text-decoration-none" href="${pager.link(sort='id', order='toggle')}" title="${translate('Ordering using this column')}">
                <span class="${pager.header_class('id')}"></span>
                ${translate('Id')}
            </a>
        </th>
        <th>
            <a class="partial-link text-decoration-none" href="${pager.link(sort='title', order='toggle')}" title="${translate('Ordering using this column')}">
                <span class="${pager.header_class('title')}"></span>
                ${translate('Title')}
            </a>
        </th>
        <th>
            <a class="partial-link text-decoration-none" href="${pager.link(sort='status', order='toggle')}" title="${translate('Ordering using this column')}">
                <span class="${pager.header_class('status')}"></span>
                ${translate('Status')}
            </a>
        </th>
    % if has_permission('articles.modify'):
        <th class="text-end">${translate('Actions')}</th>
    % endif
    </thead>
</table>

<div class="text-end d-flex flex-row-reverse">
${paginate.render_pages(pager, extra_class='mb-0 ms-4')}
${paginate.render_limit(pager, extra_class='mb-0')}
</div>
% else:
<div class="alert alert-info">${translate('No article.')}</div>
% endif
