# pyramid-helpers -- Helpers to develop Pyramid applications
# By: Cyril Lacoux <clacoux@easter-eggs.com>
#     Valéry Febvre <vfebvre@easter-eggs.com>
#
# https://gitlab.com/yack/pyramid-helpers
#
# SPDX-FileCopyrightText: © Cyril Lacoux <clacoux@easter-eggs.com>
# SPDX-FileCopyrightText: © Easter-eggs <https://easter-eggs.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

""" Custom predicates for Pyramid """


class EnumPredicate:
    """
    The route defined by:

    config.add_route('route-name', '/foo/{kind}/bar', enum_predicate={'kind': ('one', 'two')})

    Will only match the following urls:
     * /foo/one/bar
     * /foo/two/bar
    """

    # pylint: disable=unused-argument
    def __init__(self, params, config):
        self.names = list(params)
        self.params = params

    def __call__(self, context, request):
        matchdict = context['match']
        for name, values in self.params.items():
            if matchdict.get(name) not in values:
                return False
        return True

    def text(self):
        """ Predicate identifier """
        return str(self.params)

    phash = text


class NumericPredicate:
    """
    The route defined by:

    config.add_route('route-name', '/foo/{id}/bar', numeric_predicate='id')

    Will only match the following urls:
     * /foo/[0-9]+/bar
    """

    # pylint: disable=unused-argument
    def __init__(self, names, config):
        if isinstance(names, str):
            self.names = (names, )
        else:
            self.names = names

    def __call__(self, context, request):
        matchdict = context['match']
        for name in self.names:
            if not matchdict.get(name).isnumeric():
                return False
        return True

    def text(self):
        """ Predicate identifier """
        return str(self.names)

    phash = text


def includeme(config):
    """
    Set up standard configurator registrations. Use via:

    .. code-block:: python

    config = Configurator()
    config.include('pyramid_helpers.predicates')
    """

    config.add_route_predicate('enum_predicate', EnumPredicate)
    config.add_route_predicate('numeric_predicate', NumericPredicate)
