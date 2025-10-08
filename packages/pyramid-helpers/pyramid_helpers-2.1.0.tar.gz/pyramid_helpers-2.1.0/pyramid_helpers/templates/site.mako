<% route_name = request.matched_route.name if request.matched_route else '' %>\
<%def name="foot()">
</%def>\
<%def name="head()">
</%def>\
<!DOCTYPE html>
<html>
<head>
    <title>The Pyramid Web Application Development Framework</title>
    <meta charset="utf-8">

    <!-- Tell the browser to be responsive to screen width -->
    <meta content='width=device-width, initial-scale=1' name='viewport'>

    <link rel="shortcut icon" href="${request.static_path('pyramid_helpers:static/favicon.ico')}">

    <!-- Font Awesome -->
    <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.2.1/css/all.min.css" />

    <!-- Handlebars -->
    <script src="//cdn.jsdelivr.net/npm/handlebars@4.7.7/dist/handlebars.min.js"></script>

    <!-- Bootstrap -->
    <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" />
    <script src="//cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>

    <!-- Pyramid Helpers -->
    <script src="${request.static_path('pyramid_helpers:static/js/pyramid-helpers.globals.js')}"></script>
${self.head()}\
</head>

<body style="padding: 70px 0;">
    <header>
        <nav class="navbar navbar-dark navbar-expand-lg bg-dark fixed-top">
            <div class="container">
                <a class="navbar-brand" href="${request.route_path('index')}">
                    <img src="${request.static_path('pyramid_helpers:static/favicon.ico')}" height="32px" width="32px">
                    <span class="fs-4 p-2">Pyramid Helpers</span>
                </a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#main-navbar" aria-controls="main-navbar" aria-expanded="false" aria-label="${translate('Toggle navigation')}">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="main-navbar">
                    <ul class="nav navbar-nav navbar-start">
                        <li class="nav-item">
                            <a class="nav-link${' active' if route_name.startswith('articles.') else ''}" href="${request.route_path('articles.search')}">
                                ${translate('Articles')}
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link${' active' if route_name == 'predicates' else ''}" href="${request.route_path('predicates')}">
                                ${translate('Predicates')}
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link${' active' if route_name == 'validators' else ''}" href="${request.route_path('validators')}">
                                ${translate('Validators')}
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link${' active' if route_name == 'i18n' else ''}" href="${request.route_path('i18n')}">
                                ${translate('I18n')}
                            </a>
                        </li>
% if authenticated_user is not None:
                        <li class="nav-item">
                            <a class="nav-link${' active' if route_name == 'api-doc' else ''}" href="${request.route_path('api-doc')}">
                                ${translate('API Doc')}
                            </a>
                        </li>
% endif
                    </ul><!-- /.navbar-nav -->
                </div>
                <div class="d-flex">
% if authenticated_user is None:
                    <a class="btn btn-primary me-3" href="${request.route_path('auth.sign-in')}" title="${translate('Sign in')}">${translate('Sign in')}</a>
% else:
                    <span class="navbar-text me-3">${authenticated_user.fullname}</span>
    % if has_permission('articles.create'):
                    <a class="btn btn-success me-3" href="${request.route_path('articles.create')}" title="${translate('New article')}">${translate('New article')}</a>
    % endif
                    <a class="btn btn-primary" href="${request.route_path('auth.sign-out')}" title="${translate('Sign out')}">${translate('Sign out')}</a>
% endif
                </div>
            </div>
        </nav>
    </header>

    <div class="container">
% if not request.exception and route_name not in ('auth.sign-in', 'auth.sign-out'):
    <% breadcrumb.insert(0, (translate('Home'), request.route_path('index'))) %>\
        <nav class="my-3 lh-lg" style="--bs-breadcrumb-divider: '>';" aria-label="breadcrumb">
            <ol class="breadcrumb m-0">
    % for name, url in breadcrumb[:-1]:
                <li class="breadcrumb-item"><a class="text-decoration-none" href="${url}">${name}</a></li>
    % endfor
    <% name, url = breadcrumb[-1] %>
                <li class="breadcrumb-item active">${name}</li>
            </ol>
        </nav>
% endif
        <section>
${self.body()}\
        </section>
    </div><!-- /.container -->

    <footer class="bg-light fixed-bottom p-3 border-top">
        <div class="text-center">&copy; Copyright Cyril Lacoux, <a class="text-decoration-none" href="http://easter-eggs.com">Easter-eggs</a>.</div>
    </footer>

<!-- Handlebar templates -->
<script id="tpl-form-error" type="text/x-handlebars-template">
<div class="alert alert-danger mt-2 form-error" role="alert">
    {{message}}
</div>
</script>

<script id="tpl-loading" type="text/x-handlebars-template">
<div class="position-absolute opacity-50 top-0 start-0 w-100 h-100 bg-white" style="z-index: 1100;">
    <div class="position-absolute top-50 start-50 translate-middle">
        <i class="fa fa-cog fa-spin fa-5x"></i>
    </div>
</div>
</script>

<!-- Pyramid Helpers -->
<script src="${request.static_path('pyramid_helpers:static/js/pyramid-helpers.js')}"></script>
${self.foot()}\
</body>
</html>
