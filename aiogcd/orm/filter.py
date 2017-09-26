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

    def set_offset_limit(self, offset, limit):
        """Set offset and limit for Filter query.

        :param offset: can be int or None(to avoid setting offset)
        :param limit: can be int or None(to avoid setting limit)
        :return: True: always returns True
        """
        if offset:
            if not isinstance(offset, int):
                raise TypeError(
                    'offset is expected to be int, {} passed'.format(
                        type(offset)))

            self['query']['offset'] = offset

        if limit:
            if not isinstance(limit, int):
                raise TypeError(
                    'limit is expected to be int, {} passed'.format(
                        type(limit)))

            self['query']['limit'] = limit

        return True

    async def get_entity(self, gcd: GcdConnector):
        """Return a GcdModel instance from the supplied filter.

        :param gcd: GcdConnector instance.
        :return: GcdModel object or None in case no entity was found.
        """
        entity = await gcd.get_entity(self)
        return None if entity is None else self._model(entity)

    async def get_entities(
            self, gcd: GcdConnector, offset=None, limit=None) -> list:
        """Returns a list containing GcdModel instances from the supplied
        filter.

        :param gcd: GcdConnector instance.
        :param offset: integer to specify how many rows to skip
        :param limit: integer to specify max number of rows to return
        :return: list containing GcdModel objects.
        """
        self.set_offset_limit(offset, limit)
        return [self._model(ent) for ent in await gcd.get_entities(self)]

    async def get_key(self, gcd):
        return await gcd.get_key(self)

    async def get_keys(self, gcd, offset=None, limit=None):
        self.set_offset_limit(offset, limit)
        return await gcd.get_keys(self)
