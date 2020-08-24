from urllib.parse import urlencode, quote_plus
from asyncio_extras.contextmanager import async_contextmanager
from asyncio_extras.asyncyield import yield_
import asyncio
import aiohttp
import datetime
import json
import jwt
import logging
import time
import typing

ScopeList = typing.List[str]
JWT_GRANT_TYPE = 'urn:ietf:params:oauth:grant-type:jwt-bearer'
GCLOUD_TOKEN_DURATION = 3600
MISMATCH = "Project name passed to Token does not match service_file's " \
           "project_id."


@async_contextmanager
async def ensure_session(session):

    if session:
        await yield_(session)
    else:
        async with aiohttp.ClientSession() as session:
            await yield_(session)


class ServiceAccountToken():

    def __init__(self, project_id: str, service_file: str,
                 scopes: ScopeList, session: aiohttp.ClientSession = None):

        self.project_id = project_id

        self.service_data = None
        with open(service_file) as f:
            self.service_data = json.loads(f.read())

        # sanity check
        assert self.project_id == self.service_data['project_id'], MISMATCH

        self.scopes = list(scopes)

        self.session = session
        self.access_token = None
        self.access_token_duration = None
        self.access_token_acquired_at = None

        self.acquiring = None

    async def get(self):
        await self.ensure_token()
        return self.access_token

    async def connect(self):
        # Really just an alias of self.get
        token_ = await self.get()
        logging.info('Token is valid.')
        return token_

    async def ensure_token(self):
        if self.acquiring:
            await self.acquiring

        elif not self.access_token:
            self.acquiring = asyncio.ensure_future(
                self._acquire_access_token())
            await self.acquiring

        else:
            now = datetime.datetime.now()
            delta = (now - self.access_token_acquired_at).total_seconds()
            if delta > self.access_token_duration / 2:
                self.acquiring = asyncio.ensure_future(
                    self._acquire_access_token())

                await self.acquiring

    async def _acquire_access_token(self):
        data = await self._acquire_token()

        access_token = data['access_token']
        expires_in = data['expires_in']

        self.access_token = access_token
        self.access_token_duration = expires_in
        self.access_token_acquired_at = datetime.datetime.now()
        self.acquiring = None

        return True

    async def _acquire_token(self):
        assertion = self._generate_assertion()
        url = self.service_data['token_uri']

        headers = {'content-type': 'application/x-www-form-urlencoded'}
        payload = {
            'grant_type': JWT_GRANT_TYPE,
            'assertion': assertion
        }
        payload = urlencode(payload, quote_via=quote_plus)

        async with ensure_session(self.session) as s:
            response = await s.post(
                url,
                data=payload,
                headers=headers,
                timeout=60
            )
            json = await response.json()

        return json

    def _generate_assertion(self):
        payload = self._make_gcloud_oauth_body(
        )

        jwt_token = jwt.encode(
            payload,
            self.service_data['private_key'],
            algorithm='RS256'
        )

        return jwt_token

    def _make_gcloud_oauth_body(self):
        uri = self.service_data['token_uri']
        client_email = self.service_data['client_email']

        now = int(time.time())

        return {
            'aud': uri,
            'exp': now + GCLOUD_TOKEN_DURATION,
            'iat': now,
            'iss': client_email,
            'scope': ' '.join(self.scopes),
        }


async def _smoke_test(project, service_file, scopes=None):

    import aiohttp
    DEFAULT_SCOPES = {
        'https://www.googleapis.com/auth/datastore',
        'https://www.googleapis.com/auth/cloud-platform'
    }
    scopes = scopes or list(DEFAULT_SCOPES)

    with aiohttp.ClientSession() as session:

        token = ServiceAccountToken(
            project,
            service_file,
            session=session,
            scopes=scopes
        )

        result = await token.connect()

    print('success: {}'.format(result))


if __name__ == '__main__':
    import sys
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_smoke_test(*sys.argv[1:]))
