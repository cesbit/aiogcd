"""filter.py

Created on: May 19, 2017
    Author: Jeroen van der Heijden <jeroen@transceptor.technology>
"""
from ..connector.key import Key
from ..connector import GcdConnector


class Filter(dict):

    def __init__(self, model, *filters, has_ancestor=None, key=None):
        self._model = model
        filters = list(filters)

        if has_ancestor is not None:
            assert isinstance(has_ancestor, Key), \
                'Keyword argument \'has_ancestor\' should be of type ' \
                '\'Key\' but found type {!r}' \
                .format(has_ancestor.__class__.__name__)

            filters.append({
                'property': {'name': '__key__'},
                'value': {'keyValue': has_ancestor.get_dict()},
                'op': 'HAS_ANCESTOR'})

        if key is not None:
            assert isinstance(key, Key), \
                'Keyword argument \'key\' should be of type \'Key\' ' \
                'but found type {!r}' \
                .format(key.__class__.__name__)
            filters.append({
                'property': {'name': '__key__'},
                'value': {'keyValue': key.get_dict()},
                'op': 'EQUAL'})

        filter_dict = {'query': {'kind': [{'name': self._model.get_kind()}]}}

        if len(filters) == 1:
            filter_dict['query']['filter'] = {
                'propertyFilter': filters[0]
            }
        elif len(filters) > 1:
            filter_dict['query']['filter'] = {
                'compositeFilter': {
                    'op': 'AND',
                    'filters': [{'propertyFilter': f} for f in filters]
                }
            }

        super().__init__(**filter_dict)

    async def get_entity(self, gcd: GcdConnector):
        """Return a GcdModel instance from the supplied filter.

        :param gcd: GcdConnector instance.
        :return: GcdModel object or None in case no entity was found.
        """
        entity = await gcd.get_entity(self)
        return None if entity is None else self._model(entity)

    async def get_entities(self, gcd: GcdConnector) -> list:
        """Returns a list containing GcdModel instances from the supplied filter.

        :param gcd: GcdConnector instance.
        :return: list containing GcdModel objects.
        """
        return [self._model(ent) for ent in await gcd.get_entities(self)]

    async def get_key(self, gcd):
        return await gcd.get_key(self)

    async def get_keys(self, gcd):
        return await gcd.get_keys(self)
