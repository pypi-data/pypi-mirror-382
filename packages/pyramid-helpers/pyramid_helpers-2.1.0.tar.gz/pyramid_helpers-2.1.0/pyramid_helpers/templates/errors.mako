<%inherit file="/site.mako" />\
<div class="alert alert-danger">
    <strong>${translate('Error:')}</strong> ${translate(request.exception.message or request.exception.explanation)}
% if request.exception.code == 403 and request.authenticated_user is None:
    <br />
    <% sign_in_link = '<a href="{0}" class="alert-link">{1}</a>'.format(request.route_path('auth.sign-in'), translate('signin[action]')) %>
    ${translate('Authentication is required to access this resource, please {0} in order to proceed.').format(sign_in_link) | n}
% endif
</div>
