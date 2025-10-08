<%inherit file="/site.mako" />\
<div class="alert alert-info">
    <h4 class="alert-heading">${translate('You have been successfully logged out!')}</h4>
    ${translate('You may return to <a href="{0}" class="alert-link">home page</a>.').format(request.route_path('index')) | n}
</div>
