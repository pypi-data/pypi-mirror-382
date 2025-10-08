<%!
import markdown
%>\
<%inherit file="/site.mako" />
<%def name="foot()">
${parent.foot()}\
    <!-- API-Doc App -->
    <script src="${request.static_path('pyramid_helpers:static/js/api-doc.js')}"></script>
</%def>\
<%def name="head()">
${parent.head()}\
    <!-- API-Doc Libraries -->
    % for url in libraries:
        % if url.endswith('.css'):
    <link href="${url}" rel="stylesheet" />
        % elif url.endswith('.js'):
    <script src="${url}"></script>
        % endif
    % endfor

    <!-- API-Doc Styles -->
    <link href="${request.static_path('pyramid_helpers:static/css/api-doc-bs4.css')}" rel="stylesheet" />

    <!-- API-Doc Constants -->
    <script>
const API_DOC_BOOTSTRAP_VERSION = 4;
    </script>
</%def>\
\
<%def name="parameter_row(service_id, data)">
<%
    id = 'api-doc-input-{0}-{1}'.format(data['name'].replace('_', '-'), service_id)

    type_label = '{0} of {1}'.format(data['type'], data['items']['type']) if data['type'] in ('ForEach', 'NumberList', 'StringList',) and data['items'] else data['type']
    if data.get('format') is not None:
        type_label = '{0} <mark> {1} </mark>'.format(type_label, data['format'])
    if data.get('min') is not None and data.get('max') is not None:
        type_label = '{0} <mark> {1} <= x <= {2} </mark>'.format(type_label, data['min'], data['max'])
    elif data.get('min') is not None:
        type_label = '{0} <mark> x >= {1} </mark>'.format(type_label, data['min'])
    elif data.get('max') is not None:
        type_label = '{0} <mark> x <= {1} </mark>'.format(type_label, data['max'])

    required_tr_class = ' form-required danger' if data['required'] else ''
    required_input = ' required' if data['required'] else ''
%>\
\
<tr class="form-group${required_tr_class}">
    <td><label for="${id}">${data['name']}</label></td>
    <td>
    % if data['type'] in ('Date', 'DateTime'):
        <div id="datetimepicker-${id}" class="input-group input-group-sm date ${data['type'].lower()}picker" data-target-input="nearest">
            <input type="text" class="form-control form-control-sm" id="${id}" name="${data['name']}" data-date-format="${data['format']}"${required_input} />
            <div class="input-group-append" data-target="#datetimepicker-${id}" data-toggle="datetimepicker">
                <span class="input-group-text"><i class="fa fa-calendar"></i></span>
            </div>
        </div>
    % elif data['type'] == 'Int':
        <input type="number" class="form-control form-control-sm" min="${data.get('min') or -4294967295}" max="${data.get('max') or 4294967295}" id="${id}" name="${data['name']}"${required_input} />
    % elif data['type'] == 'OneOf':
        <select class="form-control form-control-sm selectpicker" id="${id}" name="${data['name']}" ${required_input} data-minimum-results-for-search="Infinity">
            <option value=""></option>
        % for value in data['values']:
            <option value="${value}">${value}</option>
        % endfor
        </select>
    % elif data['type'] in ('ForEach', 'NumberList', 'StringList',) and data['items'] and data['items']['type'] == 'OneOf':
        <select class="form-control form-control-sm selectpicker" multiple="multiple" id="${id}" name="${data['name']}"${required_input} data-minimum-results-for-search="Infinity">
            <option value=""></option>
        % for value in data['items']['values']:
            <option value="${value}">${value}</option>
        % endfor
        </select>
    % elif data['type'] == 'StringBool':
        <select class="form-control form-control-sm selectpicker" id="${id}" name="${data['name']}" ${required_input} data-minimum-results-for-search="Infinity">
            <option value=""></option>
            <option value="false">${translate('False')}</option>
            <option value="true">${translate('True')}</option>
        </select>
    % elif 'password' in data['name'].lower():
        <input type="password" class="form-control form-control-sm" id="${id}" name="${data['name']}"${required_input} />
    % else:
        <input type="text" class="form-control form-control-sm" id="${id}" name="${data['name']}"${required_input} />
    % endif
    </td>
    <td>${data['description'] or '-'}</td>
    <td>${data['parameter_type']}</td>
    <td>${type_label | n}</td>
    <td>${data['default'] if data['default'] not in (None, [], ()) else '-'}</td>
</tr>
</%def>\
\
<div class="row">
    <div class="col-md-12 d-flex flex-row justify-content-between mb-3">
        <form class="form-inline">
            <div class="input-group input-group-sm">
                <input class="form-control" type="search" id="api-doc-input-filter" placeholder="${translate('Filter')}" aria-label="${translate('Filter')}">
                <div class="input-group-append">
                    <div class="input-group-text">
                        <i class="fas fa-filter"></i>
                    </div>
                </div>
            </div>
        </form>

        <button class="btn btn-primary btn-sm" data-toggle="modal" data-target="#api-doc-help-modal">
            Help <i class="fa fa-question"></i>
        </button>
    </div>
</div>

% if missing:
<div class="alert alert-warning alert-dismissible fade show" role="alert">
    <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">&times;</span>
    </button>
    <h4 class="alert-heading">
        <i class="fa fa-ban"></i> ${translate('One or more optional libraries are not available!')}
    </h4>
    <ul class="list-unstyled mb-0">
    % for library in missing:
        <li>${library}</li>
    % endfor
  </ul>
</div>
% endif

% if orphans:
<div class="alert alert-warning alert-dismissible fade show">
    <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">&times;</span>
    </button>
    <h4 class="alert-heading">
        <i class="fa fa-exclamation-triangle"></i> ${translate('Orphan routes detected!')}
    </h4>
    <ul class="list-unstyled mb-0">
    % for service in orphans:
        <li>${' / '.join(service['request_methods'])} ${service['pattern']}</li>
    % endfor
    </ul>
</div>
% endif

% if len(modules):
    % for module_name, module in modules.items():
        <% module_id = 'accordion-module-' + module_name.replace('.', '-') %>
<h4 class="api-doc-module-title" data-toggle="collapse" data-target="#api-doc-${module_id}" aria-controls="api-doc-${module_id}">
    ${module['doc'].split('\n')[0] if module['doc'] is not None else translate('??? Undocumented module ???')}
    <i class="fa fa-chevron-up fa-sm float-right"></i>
</h4>

<div class="collapse show api-doc-module" id="api-doc-${module_id}" aria-multiselectable="true">
        % for service in module['services']:
            <% service_id = service['name'].replace('.', '-') %>
            % if not service['allowed'] or (service['doc'] is None and hide_undocumented):
                <% continue %>
            % endif
    <div class="card api-doc-service">
        <div class="card-header p-0 border-bottom-0">
            <h5 class="card-title api-doc-service-title" data-toggle="collapse" data-target="#api-doc-collapse-${service_id}" aria-expanded="true" aria-controls="api-doc-collapse-${service_id}">
                ## Methods
            % if service['request_methods']:
                <% method = service['request_methods'][0].lower() %>
                % for request_method in service['request_methods']:
                <span class="badge api-doc-service-method api-doc-service-method-${method}">${request_method}</span>
                % endfor
            % else:
                <% method = 'unknown' %>
                <span class="badge api-doc-service-method api-doc-service-method-unknown">???</span>
            % endif

                ## Path
                <span class="api-doc-service-path p-2">
                    ${service['pattern']}
                </span>

            % if service['doc']:
                ## Short description: 1st line of docstring
                <span class="api-doc-service-description p-2 ml-auto api-doc-service-description-${method}">
                    ${service['doc'].split('\n')[0]}
                </span>
            % endif
            </h5>
        </div>

        <div id="api-doc-collapse-${service_id}" class="collapse api-doc-service-collapse" data-parent="#api-doc-${module_id}" aria-labelledby="api-doc-heading-${service_id}">
            <div class="card-body api-doc-service-card-body-${method}">
            % if service['doc']:
                <div class="alert api-doc-service-doc-${method}">
                    <label class="mb-0">${service['doc'].split('\n')[0]}</label>
                % if len(service['doc'].split('\n')) > 1:
                    <p class="mb-0">${'<br />'.join(service['doc'].split('\n')[1:]) | n}</p>
                % endif
                </div>
            % endif
                <form action="${service['pattern']}" role="form" method="${service['request_methods'][0] if service['request_methods'] else ''}">
            % if service['parameters']:
                    <h5>${translate('Parameters')}</h5>
                    <table class="table table-sm table-hover table-borderless">
                        <thead>
                            <tr>
                                <th>${translate('Parameter')}</th>
                                <th>${translate('Value')}</th>
                                <th>${translate('Description')}</th>
                                <th>${translate('Parameter Type')}</th>
                                <th>${translate('Data Type')}</th>
                                <th>${translate('Default')}</th>
                            </tr>
                        </thead>
                        <tbody>
                % for parameter in service['parameters']:
                            ${parameter_row(service_id, parameter)}
                % endfor
                        </tbody>
                    </table>
            % endif
                    <div class="float-right">
                        <button class="btn btn-primary" type="submit">
                            <i class="fas fa-circle-notch fa-spin fa-fw mr-1 d-none"></i>
                            ${translate('Send request')}
                        </button>
                    </div>
                </form>
            </div><!-- .card-body -->
        </div><!-- .api-doc-service-collapse -->
    </div><!-- .card -->
        % endfor
</div><!-- .api-doc-module -->
    % endfor
% else:
<div class="alert alert-info" role="alert">${translate('No API services found')}</div>
% endif

<!-- Help modal -->
<div class="modal fade" id="api-doc-help-modal" tabindex="-1" role="dialog" aria-labelledby="api-doc-help-modal-label">
    <div class="modal-dialog modal-xl modal-dialog-scrollable" role="document">
        <div class="modal-content">
            <div class="modal-header">
                <h4 class="modal-title" id="api-doc-help-modal-label">${translate('Help')}</h4>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
            </div>
            <div class="modal-body">
                <ul class="nav nav-tabs" role="tablist">
                    <li class="nav-item active"><a href="#api-doc-request-methods" class="nav-link active" aria-controls="api-doc-request-methods" aria-selected="false" role="tab" data-toggle="tab">Request Methods</a></li>
                    <li class="nav-item"><a href="#api-doc-response-codes" class="nav-link" aria-controls="api-doc-response-codes" aria-selected="false" aria-selected="false" role="tab" data-toggle="tab">Response Status Codes</a></li>
                    <li class="nav-item"><a href="#api-doc-examples" class="nav-link" aria-controls="api-doc-examples" aria-selected="false" role="tab" data-toggle="tab">Examples</a></li>
                    <li class="nav-item"><a href="#api-doc-faq" class="nav-link" aria-controls="api-doc-faq" aria-selected="false" role="tab" data-toggle="tab">FAQ</a></li>
                </ul>

                <div class="tab-content">
                    <!-- Request Methods -->
                    <div role="tabpanel" class="tab-pane active" id="api-doc-request-methods">
                        <table class="table">
                            <tbody>
                                <tr>
                                    <td align="right"><span class="badge api-doc-service-method-get">GET</span></td>
                                    <td>
                                        <p>The <strong>GET</strong> method is used to **read** (or retrieve) a specific resource (by an identifier) or a collection of resources.</p>

                                        <p>In the “happy” (or non-error) path, <strong>GET</strong> returns a representation in JSON or CSV and an HTTP response code of <mark>200</mark> (OK). In an error case, it most often returns a <mark>404</mark> (NOT FOUND) or <mark>400</mark> (BAD REQUEST).</p>

                                        <p><strong>GET</strong> requests are used only to read data and not change it. Therefore, when used this way, they are considered safe. That is, they can be called without risk of data modification or corruption—calling it once has the same effect as calling it 10 times, or none at all. Additionally, <strong>GET</strong> is idempotent, which means that making multiple identical requests ends up having the same result as a single request.</p>

                                        <p>Parameters must be encoded as a query string (param1=value1&amp;param2=value2&amp;param3=value3...) and append to URL path after a '?'.</p>
                                    </td>
                                </tr>
                                <tr>
                                    <td align="right"><span class="badge api-doc-service-method-post">POST</span></td>
                                    <td>
                                        <p>The <strong>POST</strong> method is most-often utilized to **create** new resources.</p>

                                        <p>On successful creation, return HTTP status <mark>201</mark>, returning a Location header with a link to the newly-created resource.</p>

                                        <p><strong>POST</strong> is neither safe nor idempotent. It is therefore recommended for non-idempotent resource requests. Making two identical <strong>POST</strong> requests will most-likely result in two resources containing the same information.</p>

                                        <p>Parameters must be passed in request body.</p>
                                    </td>
                                </tr>
                                <tr>
                                    <td align="right"><span class="badge api-doc-service-method-put">PUT</span></td>
                                    <td>
                                        <p>The <strong>PUT</strong> method is used to **update** a specific resource (by an identifier) or a collection of resources.</p>

                                        <p>On successful update, return HTTP status <mark>200</mark> (OK).</p>

                                        <p><strong>PUT</strong> is not a safe operation, in that it modifies state on the server, but it is idempotent. In other words, if you update a resource using <strong>PUT</strong> and then make that same call again, the resource is still there and still has the same state as it did with the first call.</p>

                                        <p>Parameters must be passed in request body.</p>
                                    </td>
                                </tr>
                                <tr>
                                    <td align="right"><span class="badge api-doc-service-method-delete">DELETE</span></td>
                                    <td>
                                        <p>The <strong>DELETE</strong> method is pretty easy to understand. It is used to **delete** a resource by an identifier.</p>

                                        <p>On successful deletion, return HTTP status <mark>200</mark> (OK).</p>

                                        <p><strong>DELETE</strong> operations are idempotent. If you <strong>DELETE</strong> a resource, it's removed. Repeatedly calling <strong>DELETE</strong> on that resource ends up the same: the resource is gone.</p>

                                        <p>Parameters must be passed in request body.</p>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- Response Status Codes -->
                    <div role="tabpanel" class="tab-pane" id="api-doc-response-codes">
                        <table class="table">
                            <tbody>
                                <tr>
                                    <th align="right">200</th>
                                    <td>OK</td>
                                    <td>General success status code. This is the most common code. Used to indicate success.</td>
                                </tr>
                                <tr>
                                    <th align="right">201</th>
                                    <td>CREATED</td>
                                    <td>
                                        Successful creation occurred. Set the Location header to contain a link to the newly-created resource.
                                    </td>
                                </tr>
                                <tr>
                                    <th align="right">400</th>
                                    <td>BAD REQUEST</td>
                                    <td>
                                        General error for when fulfilling the request would cause an invalid state. Domain validation errors, missing data, etc. are some examples.
                                    </td>
                                </tr>
                                <tr>
                                    <th align="right">401</th>
                                    <td>UNAUTHORIZED</td>
                                    <td>
                                        Error code response for missing or invalid authentication token.
                                    </td>
                                </tr>
                                <tr>
                                    <th align="right">403</th>
                                    <td>FORBIDDEN</td>
                                    <td>
                                        Error code for when the user is not authorized to perform the operation or the resource is unavailable for some reason (e.g. time constraints, etc.).
                                    </td>
                                </tr>
                                <tr>
                                    <th align="right">404</th>
                                    <td>NOT FOUND</td>
                                    <td>
                                        Used when the requested resource is not found, whether it doesn't exist or if there was a <mark>401</mark> or <mark>403</mark> that, for security reasons, the service wants to mask.
                                    </td>
                                </tr>
                                <tr>
                                    <th align="right">500</th>
                                    <td>INTERNAL SERVER ERROR</td>
                                    <td>
                                        The general catch-all error when the server-side throws an exception.
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- Examples -->
                    <div role="tabpanel" class="tab-pane" id="api-doc-examples">
<%
content = translate('No examples found')
md_path = request.registry.settings.get('api_doc.examples_md_file')
if md_path:
    with open(md_path, 'r') as f:
        content = f.read()
%>
${markdown.markdown(content, extensions=['markdown.extensions.codehilite']) | n}
                    </div>

                    <!-- FAQ -->
                    <div role="tabpanel" class="tab-pane" id="api-doc-faq">
                        <h3>What is paging and how does it work?</h3>
                        <p>Paging is the process of dividing a response into several pages.</p>
                        <p>Sometime, a call to an API services returns a massive number of results. In this case, paging is useful for a better handling of the response.</p>

                        <h4>Paging parameters in request</h4>
                        <dl class="row">
                            <dt class="col-lg-4 text-lg-right">{pager_name}.sort</dt>
                            <dd class="col-lg-8">Allows you to define the sorting key to order the results by.</dd>
                            <dt class="col-lg-4 text-lg-right">{pager_name}.order</dt>
                            <dd class="col-lg-8">Allows you to define the sorting order.</dd>
                            <dt class="col-lg-4 text-lg-right">{pager_name}.limit</dt>
                            <dd class="col-lg-8">Allows you to define the number of items that will be returned in each page.</dd>
                            <dt class="col-lg-4 text-lg-right">{pager_name}.page</dt>
                            <dd class="col-lg-8">Allows you to define the number of the desired page.</dd>
                            <dd class="col-lg-8 offset-lg-4"><em>If it's greater than number of pages, no data will be returned.</em></dd>
                        </dl>

                        <h4>Paging information in response</h4>
                        <dl class="row">
                            <dt class="col-lg-4 text-lg-right">pager.name</dt>
                            <dd class="col-lg-8">Name of the pager</dd>
                            <dt class="col-lg-4 text-lg-right">pager.sort</dt>
                            <dd class="col-lg-8">Sorting key</dd>
                            <dt class="col-lg-4 text-lg-right">pager.order</dt>
                            <dd class="col-lg-8">Sorting order</dd>
                            <dt class="col-lg-4 text-lg-right">pager.limit</dt>
                            <dd class="col-lg-8">Number of items requested per page</dd>
                            <dt class="col-lg-4 text-lg-right">pager.page</dt>
                            <dd class="col-lg-8">Current page number</dd>
                            <dt class="col-lg-4 text-lg-right">pager.count</dt>
                            <dd class="col-lg-8">Number of items in current page (equal or inferior to limit)</dd>
                            <dt class="col-lg-4 text-lg-right">pager.pages</dt>
                            <dd class="col-lg-8">Total number of pages</dd>
                            <dt class="col-lg-4 text-lg-right">pager.total</dt>
                            <dd class="col-lg-8">Total number of items (all pages combined)</dd>
                        </dl>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-default" data-dismiss="modal">${translate('Close')}</button>
            </div>
        </div>
    </div>
</div>

<!-- Response modal -->
<div class="modal fade" id="api-doc-response-modal" tabindex="-1" role="dialog" aria-labelledby="api-doc-response-modal-label" aria-hidden="true">
    <div class="modal-dialog modal-xl modal-dialog-scrollable" role="document">
        <div class="modal-content">
            <div class="modal-header">
                <h4 class="modal-title" id="api-doc-response-modal-label">${translate('Response')}</h4>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
            </div>
            <div class="modal-body">
                <div id="api-doc-response-request-url">
                    <h5>${translate('Request URL')}</h5>
                    <pre class="border bg-light"></pre>
                </div>

                <div id="api-doc-response-request-data">
                    <h5>${translate('Request Data')}</h5>
                    <pre class="border bg-light"></pre>
                </div>

                <div id="api-doc-response-request-curl-cmd">
                    <h5>${translate('CURL Command')}</h5>
                    <pre class="border bg-light"></pre>
                </div>

                <div id="api-doc-response-code">
                    <h5>${translate('Response Status Code')}</h5>
                    <pre class="border bg-light"></pre>
                </div>

                <div id="api-doc-response-body">
                    <h5>${translate('Response Body')}</h5>
                    <pre class="border bg-light"></pre>
                </div>

                <div id="api-doc-response-headers">
                    <h5>${translate('Response Headers')}</h5>
                    <pre class="border bg-light"></pre>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-default" data-dismiss="modal">${translate('Close')}</button>
            </div>
        </div>
    </div>
</div>
