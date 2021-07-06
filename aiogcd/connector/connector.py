"""connector.py

Created on: May 19, 2017
   Authors: Jeroen van der Heijden <jeroen@transceptor.technology>
            jomido <https://github.com/jomido>
"""
import os
import json
import aiohttp
from .client_token import Token
from .service_account_token import ServiceAccountToken
from .entity import Entity
from .key import Key
from .utils import make_read_options

DEFAULT_SCOPES = {
    'https://www.googleapis.com/auth/datastore',
    'https://www.googleapis.com/auth/cloud-platform'
}

DEFAULT_API_ENDPOINT = 'https://datastore.googleapis.com'

DATASTORE_URL = \
    '{api_endpoint}/v1/projects/{project_id}:{method}'

_MAX_LOOPS = 128


def _get_api_endpoint():
    emu_host = os.getenv('DATASTORE_EMULATOR_HOST')
    if emu_host is None:
        return DEFAULT_API_ENDPOINT
    return 'http://{}'.format(emu_host)


class GcdConnector:

    def __init__(
            self,
            project_id,
            client_id,
            client_secret,
            token_file,
            scopes=DEFAULT_SCOPES,
            namespace_id=None):

        self.project_id = project_id
        self.namespace_id = namespace_id
        self._token = Token(
            client_id,
            client_secret,
            token_file,
            scopes)

        api_endpoint = _get_api_endpoint()

        self._run_query_url = DATASTORE_URL.format(
            api_endpoint=api_endpoint,
            project_id=self.project_id,
            method='runQuery')

        self._commit_url = DATASTORE_URL.format(
            api_endpoint=api_endpoint,
            project_id=self.project_id,
            method='commit')

        self._lookup_url = DATASTORE_URL.format(
            api_endpoint=api_endpoint,
            project_id=self.project_id,
            method='lookup')

    async def connect(self):
        await self._token.connect()

    async def insert_entities(self, entities):
        """Returns a tuple containing boolean values. Each boolean value is
        True in case of a successful mutation and False if not. The order of
        booleans is the same as the supplied tuple or list.

        Each entity must not already exist and each entity key will be updated
        with the new key in case no name/id was specified.

        :param entities: tuple or list with Entity objects
        :return: tuple containing boolean values
        """
        return await self._commit_entities_or_keys(entities, 'insert')

    # alias
    entities = insert_entities

    async def insert_entity(self, entity):
        """Returns True if successful or False if not. In case of False then
        most likely a conflict was detected.

        The entity must not already exist and the entity key will be updated
        with the new key in case no name/id was specified.

        :param entity: Entity object
        :return: Boolean
        """
        return (await self._commit_entities_or_keys([entity], 'insert'))[0]

    async def upsert_entities(self, entities):
        """Returns a tuple containing boolean values. Each boolean value is
        True in case of a successful mutation and False if not. The order of
        booleans is the same as the supplied tuple or list.

        Each entity may or may not already exist.

        :param entities: tuple or list with Entity objects
        :return: tuple containing boolean values
        """
        return await self._commit_entities_or_keys(entities, 'upsert')

    async def upsert_entity(self, entity):
        """Returns True if successful or False if not. In case of False then
        most likely a conflict was detected.

        The entity may or may not already exist.

        :param entity: Entity object
        :return: Boolean
        """
        return (await self._commit_entities_or_keys([entity], 'upsert'))[0]

    async def update_entities(self, entities):
        """Returns a tuple containing boolean values. Each boolean value is
        True in case of a successful mutation and False if not. The order of
        booleans is the same as the supplied tuple or list.

        Each entity must already exist.

        :param entities: tuple or list with Entity objects
        :return: tuple containing boolean values
        """
        return await self._commit_entities_or_keys(entities, 'update')

    async def update_entity(self, entity):
        """Returns True if successful or False if not. In case of False then
        most likely a conflict was detected.

        The entity must already exist.

        :param entity: Entity object
        :return: Boolean
        """
        return (await self._commit_entities_or_keys([entity], 'update'))[0]

    async def delete_keys(self, keys):
        """Returns a tuple containing boolean values. Each boolean value is
        True in case of a successful mutation and False if not. The order of
        booleans is the same as the supplied tuple or list.

        Each key may or may not already exist.

        :param keys: tuple or list with Key objects
        :return: tuple containing boolean values
        """
        return await self._commit_entities_or_keys(keys, 'delete')

    async def delete_key(self, key):
        """Returns True if successful or False if not. In case of False then
        most likely a conflict was detected.

        The key may or may not already exist.

        :param key: Key object
        :return: Boolean
        """
        return (await self._commit_entities_or_keys([key], 'delete'))[0]

    async def commit(self, mutations):
        """Commit mutations.

        The only supported commit mode is NON_TRANSACTIONAL.

        See the link below for information for a description of a mutation:

        https://cloud.google.com/datastore/docs/reference/
                rest/v1/projects/commit#Mutation

        :param mutations: List or tuple with mutations
        :return: tuple containing mutation results
        """
        data = {
            'mode': 'NON_TRANSACTIONAL',
            'mutations': mutations
        }
        async with aiohttp.ClientSession() as session:

            async with session.post(
                    self._commit_url,
                    data=json.dumps(data),
                    headers=await self._get_headers()) as resp:

                content = await resp.json()

                if resp.status == 200:
                    return tuple(content.get('mutationResults', tuple()))

                raise ValueError(
                        'Error while committing to the datastore: {} ({})'
                        .format(
                            content.get('error', 'unknown'),
                            resp.status
                        ))

    async def run_query(self, data):
        """Return entities by given query data.

        :param data: see the following link for the data format:
            https://cloud.google.com/datastore/docs/reference/rest/
                v1/projects/runQuery
        :return: list containing Entity objects.
        """
        results, _ = await self._run_query(data)
        return results

    async def _run_query(self, data):
        results = []
        cursor = None

        # set namespace_id if required
        if self.namespace_id:
            if 'partitionId' not in data:
                data['partitionId'] = {'namespaceId': self.namespace_id}
            elif 'namespaceId' not in data['partitionId']:
                data['partitionId']['namespaceId'] = self.namespace_id

        while True:
            async with aiohttp.ClientSession() as session:

                if cursor is not None:
                    data['query']['startCursor'] = cursor

                async with session.post(
                        self._run_query_url,
                        data=json.dumps(data),
                        headers=await self._get_headers()) as resp:

                    content = await resp.json()

                    if resp.status == 200:

                        entity_results = \
                            content['batch'].get('entityResults', [])

                        results.extend(entity_results)

                        more_results = content['batch']['moreResults']
                        cursor = content['batch']['endCursor']

                        if more_results in (
                                'NO_MORE_RESULTS',
                                'MORE_RESULTS_AFTER_LIMIT',
                                'MORE_RESULTS_AFTER_CURSOR'):
                            break

                        if more_results == 'NOT_FINISHED':
                            continue

                        raise ValueError(
                            'Unexpected value for "moreResults": {}'
                            .format(more_results))

                    raise ValueError(
                        'Error while query the datastore: {} ({})'
                        .format(
                            content.get('error', 'unknown'),
                            resp.status
                        )
                    )

        return results, cursor

    async def _get_entities_cursor(self, data):
        results, cursor = await self._run_query(data)
        return [Entity(result['entity']) for result in results], cursor

    async def get_entities(self, data):
        """Return entities by given query data.

        :param data: see the following link for the data format:
            https://cloud.google.com/datastore/docs/reference/rest/
                v1/projects/runQuery
        :return: list containing Entity objects.
        """
        results, _ = await self._run_query(data)
        return [Entity(result['entity']) for result in results]

    async def get_keys(self, data):
        data['query']['projection'] = [{'property': {'name': '__key__'}}]
        results, _ = await self._run_query(data)
        return [Key(result['entity']['key']) for result in results]

    async def get_entity(self, data):
        """Return an entity object by given query data.

        :param data: see the following link for the data format:
            https://cloud.google.com/datastore/docs/reference/rest/
                v1/projects/runQuery
        :return: Entity object or None in case no entity was found.
        """
        data['query']['limit'] = 1
        result = await self.get_entities(data)
        return result[0] if result else None

    async def get_key(self, data):
        data['query']['limit'] = 1
        result = await self.get_keys(data)
        return result[0] if result else None

    async def get_entities_by_kind(self, kind, offset=None, limit=None,
                                   cursor=None):
        """Returns entities by kind.

        When a limit is set, this function returns a list and a cursor.
        If no limit is used, then only the list will be returned.
        """
        query = {'kind': [{'name': kind}]}
        data = {'query': query}
        if cursor:
            query['startCursor'] = cursor
        if offset:
            query['offset'] = offset

        if limit is None:
            return await self.get_entities(data)
        else:
            query['limit'] = limit
            return await self._get_entities_cursor(data)

    async def get_entities_by_keys(self, keys, missing=None, deferred=None,
                                   eventual=False):
        """Returns entity objects for the given keys or None in case no
        entity is found.

        :param keys: list of Key objects
        :return: list of Entity objects or None.
        """
        read_options = make_read_options(eventual=eventual)

        def data():
            return json.dumps({
                'readOptions': read_options,
                'keys': [k.get_dict() for k in keys],
            })

        if missing is not None and missing != []:
            raise ValueError('missing must be None or an empty list')

        if deferred is not None and deferred != []:
            raise ValueError('deferred must be None or an empty list')

        attempts = 0
        entities = []
        while keys and attempts < _MAX_LOOPS:
            attempts += 1
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        self._lookup_url,
                        data=data(),
                        headers=await self._get_headers()) as resp:

                    content = await resp.json()
                    entities.extend(Entity(result['entity']) for result in
                                    content.get('found', []))

                    if missing is not None:
                        missing.extend(result['entity'] for result in
                                       content.get('missing', []))

                    deferred_keys = [Key(result) for result in
                                     content.get('deferred', [])]

                    if deferred is not None:
                        deferred.extend(deferred_keys)
                        break

                    keys = deferred_keys

        if entities:
            return entities

    async def get_entity_by_key(self, key, missing=None, deferred=None,
                                eventual=False):
        """Returns an entity object for the given key or None in case no
        entity is found.

        :param key: Key object
        :return: Entity object or None.
        """
        entity = await self.get_entities_by_keys([key], missing, deferred,
                                                 eventual)
        if entity:
            return entity[0]

    async def _get_headers(self):
        token = await self._token.get()
        return {
            'Authorization': 'Bearer {}'.format(token),
            'Content-Type': 'application/json'
        }

    @staticmethod
    def _check_mutation_result(entity_or_key, mutation_result):
        if 'key' in mutation_result:
            # The automatically allocated key.
            # Set only when the mutation allocated a key.
            entity_or_key.key = Key(mutation_result['key'])

        return not mutation_result.get('conflictDetected', False)

    async def _commit_entities_or_keys(self, entities_or_keys, method):
        mutations = [
            {method: entity_or_key.get_dict()}
            for entity_or_key in entities_or_keys]

        mutations_results = await self.commit(mutations)

        return tuple(
            self._check_mutation_result(entity_or_key, mutation_result)
            for entity_or_key, mutation_result
            in zip(entities_or_keys, mutations_results))


class GcdServiceAccountConnector(GcdConnector):
    def __init__(
            self,
            project_id,
            service_file,
            session=None,
            scopes=None,
            namespace_id=None):

        scopes = scopes or list(DEFAULT_SCOPES)
        self.project_id = project_id
        self.namespace_id = namespace_id

        self._token = ServiceAccountToken(project_id, service_file, scopes,
                                          session)

        api_endpoint = _get_api_endpoint()

        self._run_query_url = DATASTORE_URL.format(
            api_endpoint=api_endpoint,
            project_id=self.project_id,
            method='runQuery')

        self._commit_url = DATASTORE_URL.format(
            api_endpoint=api_endpoint,
            project_id=self.project_id,
            method='commit')

        self._lookup_url = DATASTORE_URL.format(
            api_endpoint=api_endpoint,
            project_id=self.project_id,
            method='lookup')
