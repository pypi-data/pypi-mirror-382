<%!
labels = {
    'draft': 'warning',
    'published': 'success',
    'refused': 'danger',
}
%>\
<%inherit file="../site.mako" />\
<div class="card">
    <div class="card-header position-relative">
        <h2 class="card-title h5 pt-2">${translate('Article #{0}').format(article.id)}</h2>
        <small>${format_date(article.creation_date, format='long')} ${translate('by {0}').format(article.author.fullname)}</small>
% if has_permission('articles.modify'):
        <span class="badge bg-${labels[article.status]} position-absolute top-0 end-0 m-2">${translate(article.status.capitalize())}</span>
% endif
    </div>

    <div class="card-body">
        <p>${article.text.replace('\n', '<br />') | n}</p>
    </div>
% if has_permission('articles.modify'):

    <div class="card-footer d-flex">
    % if has_permission('articles.delete'):
        <a class="btn btn-danger me-auto" href="${request.route_path('articles.delete', article=article.id)}" title="${translate('Delete article {0}').format(article.title)}">${translate('Delete')}</a>
    % endif
        <a class="btn btn-primary" href="${request.route_path('articles.modify', article=article.id)}" title="${translate('Edit article {0}').format(article.title)}">${translate('Edit')}</a>
    </div>
% endif
</div>
