/*
 * pyramid-helpers -- Helpers to develop Pyramid applications
 * By: Cyril Lacoux <clacoux@easter-eggs.com>
 *     Valéry Febvre <vfebvre@easter-eggs.com>
 *
 * https://gitlab.com/yack/pyramid-helpers
 *
 * SPDX-FileCopyrightText: © Cyril Lacoux <clacoux@easter-eggs.com>
 * SPDX-FileCopyrightText: © Easter-eggs <https://easter-eggs.com>
 *
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

/* ESLint options */
/* global API_DOC_BOOTSTRAP_VERSION */
/* global apiErrorCallback, clearFormErrors, getScrollable, getStylePropertyValue, notify, translate, setFormErrors */
/* exported ApiDoc */


/*
 * Global initialization
 */
const ApiDoc = function() {
    const BS_DISPLAY_NONE = API_DOC_BOOTSTRAP_VERSION == 3 ? 'hidden' : 'd-none';

    const RE_ROUTE = /(\{[_a-zA-Z][^{}]*(?:\{[^{}]*\}[^{}]*)*\})/g;
    const RE_ROUTE_OLD = /(:[_a-zA-Z]\w*)/g;

    let filterInput = document.getElementById('api-doc-input-filter');
    let responseModal = document.getElementById('api-doc-response-modal');

    function onFilterInputChange(_e) {
        let tokens = filterInput.value.split(' ')
            .filter(function(token, _i, _array) {
                return token !== '';
            })
            .map(function(token, _i, _array) {
                return token.toLowerCase();
            });

        let regex = new RegExp(tokens.join('|'), 'g');

        document.querySelectorAll('.api-doc-service').forEach(element => {
            let path = element.querySelector('span.api-doc-service-path').innerText.toLowerCase();
            let description = element.querySelector('span.api-doc-service-description').innerText.toLowerCase();

            if (path.match(regex) || description.match(regex)) {
                element.classList.remove(BS_DISPLAY_NONE);
            }
            else {
                element.classList.add(BS_DISPLAY_NONE);
            }
        });

        document.querySelectorAll('.api-doc-module-title').forEach(element => {
            let group = element.nextElementSibling;

            let hiddenChildElementCount = [...group.children].filter(function(child, _i, _array) {
                return child.classList.contains(BS_DISPLAY_NONE);
            }).length;

            if (hiddenChildElementCount == group.childElementCount) {
                element.classList.add(BS_DISPLAY_NONE);
            }
            else {
                element.classList.remove(BS_DISPLAY_NONE);
            }
        });
    }

    function showResponse(action, method, data, response, responseData) {
        let curlCmd;
        let pre;

        // Construct curl command
        curlCmd = 'curl';
        if (!data.format || data.format === 'json') {
            curlCmd += " -H 'Accept:application/json'";
        }
        else if (data.format === 'csv') {
            curlCmd += " -H 'Accept:text/csv'";
        }

        curlCmd += ' -X ' + method;

        if (method != 'GET') {
            data.forEach((value, key) => {
                curlCmd += " \\\n    -d '" + key + '=' + decodeURIComponent(value) + "'";
            });
        }

        curlCmd += " \\\n    '" + action + "'";

        // Request URL
        responseModal.querySelector('#api-doc-response-request-url pre').innerText = action;

        // curl command
        responseModal.querySelector('#api-doc-response-request-curl-cmd pre').innerText = curlCmd;

        // Request Data
        pre = responseModal.querySelector('#api-doc-response-request-data pre');

        if (method != 'GET') {
            let jsonData = {};

            data.forEach((value, key) => {
                if (!(key in jsonData)) {
                    jsonData[key] = value;
                    return;
                }
                if (!Array.isArray(jsonData[key])) {
                    jsonData[key] = [jsonData[key]];
                }
                jsonData[key].push(value);
            });

            pre.innerHTML = syntaxHighlight(JSON.stringify(jsonData, undefined, 4));
            pre.parentElement.classList.remove(BS_DISPLAY_NONE);
        }
        else {
            pre.parentElement.classList.add(BS_DISPLAY_NONE);
        }

        // Response Code
        pre = responseModal.querySelector('#api-doc-response-code pre');

        pre.innerText = response.status;
        if (response.status < 400) {
            pre.classList.remove('api-doc-failure');
            pre.classList.add('api-doc-success');
        }
        else {
            pre.classList.remove('api-doc-success');
            pre.classList.add('api-doc-failure');
        }

        // Response Body
        pre = responseModal.querySelector('#api-doc-response-body pre');

        let link = document.createElement('A');
        link.innerHTML = '<i class="fa fa-download fa-fw"> </i>';
        link.setAttribute('download', 'response.json');
        link.style.position = 'absolute';
        link.style.right = '24px';

        if (typeof(responseData) === 'object') {
            pre.innerHTML = syntaxHighlight(JSON.stringify(responseData, undefined, 4));

            link.setAttribute('href', 'data:application/json;charset=utf8,' + encodeURIComponent(responseData));
        }
        else {
            pre.innerText = responseData;

            link.setAttribute('href', 'data:text/plain;charset=utf8,' + encodeURIComponent(responseData));
        }

        pre.prepend(link);

        // Response Headers
        const headers = [];
        for (const pair of response.headers.entries()) {
            headers.push(`${pair[0]}: ${pair[1]}`);
        }
        responseModal.querySelector('#api-doc-response-headers pre').innerText = headers.join('\n');

        if (API_DOC_BOOTSTRAP_VERSION < 5) {
            $(responseModal).modal('show');
        }
        else {
            bootstrap.Modal.getOrCreateInstance(responseModal).show();
        }
    }

    function syntaxHighlight(json) {
        json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)/g, function(match) {
            let cls = 'number';
            if (match.startsWith('"')) {
                if (match.endsWith(':')) {
                    cls = 'key';
                }
                else {
                    cls = 'string';
                }
            }
            else if (match == 'true' || match == 'false') {
                cls = 'boolean';
            }
            else if (match == 'null') {
                cls = 'null';
            }
            return '<span class="' + cls + '">' + match + '</span>';
        });
    }

    filterInput.onchange = onFilterInputChange;
    filterInput.onkeyup = onFilterInputChange;

    responseModal.addEventListener('show.bs.modal', _e => {
        responseModal.querySelector('.modal-body').scrollTop = 0;
    });

    document.querySelectorAll('.api-doc-module.collapse').forEach(element => {
        element.addEventListener('show.bs.collapse', e => {
            if (e.target != element) {
                // Event was triggered by a child
                return;
            }

            let icon = e.target.previousElementSibling.querySelector('i, [data-fa-i2svg]');

            icon.classList.remove('fa-chevron-down');
            icon.classList.add('fa-chevron-up');
        });

        element.addEventListener('hide.bs.collapse', e => {
            if (e.target != element) {
                // Event was triggered by a child
                return;
            }

            let icon = e.target.previousElementSibling.querySelector('i, [data-fa-i2svg]');

            icon.classList.remove('fa-chevron-up');
            icon.classList.add('fa-chevron-down');
        });
    });

    document.querySelectorAll('.api-doc-service-collapse.collapse').forEach(element => {
        element.addEventListener('shown.bs.collapse', e => {
            // Scroll to target
            let scrollable = getScrollable(e.target.parentElement);
            if (scrollable) {
                let paddingTop = getStylePropertyValue(scrollable, 'padding-top', true);
                scrollable.scrollTo({top: e.target.parentElement.offsetTop - paddingTop - 20, behaviour: 'smooth'});
            }
        });
    });

    document.querySelectorAll('.api-doc-service form').forEach(element => {
        element.onsubmit = function(e) {
            e.preventDefault();

            let self = this;
            let matches;

            let action = self.getAttribute('action');
            let method = self.getAttribute('method').toUpperCase();

            clearFormErrors(self);

            if (!method) {
                notify.error(translate('Invalid API service: missing request method'));
                return;
            }

            // Show spinner icon from submit button
            e.submitter.querySelector('i').classList.toggle(BS_DISPLAY_NONE);

            let data = new FormData(self);

            function replacePredicate(match, predicate) {
                action = action.replace(match, data.get(predicate));
                data.delete(predicate);
            }

            // Map URL path pattern with input values
            matches = action.match(RE_ROUTE) || [];
            matches.map(match => {
                // remove '{' and '}' characters (first and last positions)
                let predicate = match.slice(1, -1);
                // remove expression if exists like in {name:expr} pattern
                predicate = predicate.split(':')[0];

                replacePredicate(match, predicate);
            });

            // Map URL with input values (old pattern language)
            matches = action.match(RE_ROUTE_OLD) || [];
            matches.map(match => {
                // Remove ':' character (first position)
                let predicate = match.slice(1);

                replacePredicate(match, predicate);
            });

            // Add data to query params
            if (method == 'GET') {
                action = new URL(action, document.location);

                data.forEach((value, key) => {
                    action.searchParams.append(key, value);
                });
            }

            fetch(action, {
                method: method,
                body: method == 'GET' ? null : data,
            }).then(async response => {
                // Hide spinner icon from submit button
                e.submitter.querySelector('i').classList.toggle(BS_DISPLAY_NONE);

                // Check for error response
                if (!response.ok && response.status != 400) {
                    return Promise.reject(response);
                }

                const isJson = response.headers.get('content-type')?.includes('application/json');
                let responseData;
                if (isJson) {
                    try {
                        responseData = await response.json();
                        if (responseData.errors) {
                            setFormErrors(self, responseData.errors);
                        }
                    }
                    catch {
                        responseData = await response.text();
                    }
                }
                else {
                    responseData = await response.text();
                }

                showResponse(action, method, data, response, responseData);
            }).catch(async response => {
                apiErrorCallback(response);
            });
        };
    });

    // Initialize filter
    onFilterInputChange();

    return {};
}();
