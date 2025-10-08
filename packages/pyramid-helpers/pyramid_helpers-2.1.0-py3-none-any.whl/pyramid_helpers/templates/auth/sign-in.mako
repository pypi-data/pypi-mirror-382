<%namespace name="form" file="/form-tags.mako"/>\
<!DOCTYPE html>
<html lang="${request.locale_name}">
<head>
    <title>Pyramid-Helpers | ${title}</title>
    <meta charset="utf-8">

    <!-- Tell the browser to be responsive to screen width -->
    <meta content="width=device-width, initial-scale=1" name="viewport">

    <link rel="shortcut icon" href="${request.static_path('pyramid_helpers:static/favicon.ico')}">

    <!-- Bootstrap -->
    <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" />
    <script src="//cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>

    <!-- Custom -->
    <link href="${request.static_path('pyramid_helpers:static/css/sign-in.css')}" rel="stylesheet" />
</head>
<body>

<main class="form-signin w-100 m-auto">
    <a href="${request.route_path('index')}" class="btn btn-outline-secondary btn-lg w-100 mb-3" title="Pyramid-Helpers">
        <span class="fw-bold">Pyramid-Helpers</span>
    </a>
    <%form:form name="signin" action="${request.route_path('auth.sign-in')}" method="post" role="form">
        <%form:hidden name="redirect" />
        <h1 class="h3 mb-3 fw-normal text-center">${title}</h1>

        <div class="form-floating">
            <%form:text name="username" id="username" class_="form-control" placeholder="${translate('Username')}" />
            <label for="username">${translate('Username')}</label>
        </div>

        <div class="form-floating">
            <%form:password name="password" id="password" class_="form-control" placeholder="${translate('Password')}" />
            <label for="password">${translate('Password')}</label>
        </div>

        <button class="mt-3 w-100 btn btn-lg btn-primary" type="submit">${translate('Sign in')}</button>
        <p class="mt-5 mb-3 text-center text-muted">&copy; Copyright Cyril Lacoux, <a href="http://easter-eggs.com">Easter-eggs</a>.</p>
    </%form:form>
</main>

</body>
</html>

