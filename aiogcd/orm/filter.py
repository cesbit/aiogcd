"""filter.py

Created on: May 19, 2017
    Author: Jeroen van der Heijden <jeroen@transceptor.technology>
"""
from ..connector.key import Key
from ..connector import GcdConnector


class Filter(dict):

    def __init__(self, model, *filters, has_ancestor=None, key=None):
        self._model = model
        self._cursor = None
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

        if self._model.__namespace__:
            filter_dict['partitionId'] = {
                'namespaceId': self._model.__namespace__
            }

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

    def _set_start_cursor(self, start_cursor):
        if start_cursor:
            if not isinstance(start_cursor, str):
                raise TypeError(
                    'start_cursor is expected to be str, {} passed'.format(
                        type(start_cursor)))
            self['query']['startCursor'] = start_cursor

    def _set_offset(self, offset):
        if offset:
            if not isinstance(offset, int):
                raise TypeError(
                    'offset is expected to be int, {} passed'.format(
                        type(offset)))

            self['query']['offset'] = offset

    def _set_limit(self, limit):
        if limit:
            if not isinstance(limit, int):
                raise TypeError(
                    'limit is expected to be int, {} passed'.format(
                        type(limit)))

            self['query']['limit'] = limit

    @property
    def cursor(self):
        return self._cursor

    def order_by(self, *order):
        self['query']['order'] = [
            {
                'property': {'name': p[0]},
                'direction': p[1]
            } if isinstance(p, tuple) else {
                'property': {'name': p.name},
                'direction': 'DIRECTION_UNSPECIFIED'
            }
            for p in order
        ]
        return self

    def limit(self, limit, start_cursor=None):
        self._set_limit(limit)
        self._set_start_cursor(start_cursor)
        return self

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
        self._set_offset(offset)
        self._set_limit(limit)
        entities, cursor = await gcd._get_entities_cursor(self)
        self._cursor = cursor
        return [self._model(ent) for ent in entities]

    async def get_key(self, gcd: GcdConnector):
        """Return a Gcd key from the supplied filter.

        :param gcd: GcdConnector instance.
        :return: GcdModel key or None in case no entity was found.
        """
        return await gcd.get_key(self)

    async def get_keys(
            self, gcd: GcdConnector, offset=None, limit=None) -> list:
        """Returns a list containing Gcd keys from the supplied filter.

        :param gcd: GcdConnector instance.
        :param offset: integer to specify how many keys to skip
        :param limit: integer to specify max number of keys to return
        :return: list containing Gcd key objects.
        """
        self._set_offset(offset)
        self._set_limit(limit)
        return await gcd.get_keys(self)

    def set_offset_limit(self, offset, limit):
        """Set offset and limit for Filter query.
        :param offset: can be int or None(to avoid setting offset)
        :param limit: can be int or None(to avoid setting limit)
        :return: True: always returns True
        """
        self._set_offset(offset)
        self._set_limit(limit)
        return True
