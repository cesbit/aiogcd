"""token.py

Created on: May 19, 2017
    Author: Jeroen van der Heijden <jeroen@transceptor.technology>
"""
import os
import time
import json
import asyncio
import logging
import aiohttp
from urllib.parse import urlencode


AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'


class Token:

    _REQUIRED_TOKEN_FIELDS = {
        'refresh_token',
        'access_token',
        'scopes',
        'token_type',
        'expires_in',
        'timestamp'
    }

    def __init__(
            self,
            client_id,
            client_secret,
            token_file,
            scopes):
        self._lock = asyncio.Lock()
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_file = token_file
        self._scopes = set(scopes)
        self._token = self._read_token_file()
        self._update_refresh_ts()

    def _update_refresh_ts(self):
        """Update _refresh_ts property which is set to the token initial
        timestamp plus half the expire time. The property is used to check
        if a token refresh is required.

        :return: None
        """
        self._refresh_ts = None if self._token is None else \
            self._token['timestamp'] + self._token['expires_in'] // 2

    def _read_token_file(self):
        """Read the specified token json file if available, checks the data and
        returns the token information.

        :return: None if the token file does not exist, a ValueError is raised
                 when the token file is not valid and a token dict is returned
                 if successful.
        """
        if not self._token_file.endswith('.json'):
            raise ValueError(
                'Invalid token file: {}, expecting a .json file.'
                .format(self._token_file))

        if os.path.isfile(self._token_file):
            with open(self._token_file, 'r') as f:
                token = json.load(f)

            missing = self._REQUIRED_TOKEN_FIELDS - set(token.keys())
            if missing:
                raise ValueError(
                    'Invalid token file: {} (fields are missing: {}).'
                    .format(self._token_file, ', '.join(missing))
                )

            scopes = set(token['scopes'])
            if scopes ^ self._scopes:
                raise ValueError(
                    'Invalid scopes defined in token file: {file}.\n'
                    'Expecting "{expecting}" but found "{found}".'.format(
                        file=self._token_file,
                        expecting=' '.join(self._scopes),
                        found=' '.join(scopes)
                    )
                )
            return token
        return None

    async def get(self):
        """Returns the access token. If _refresh_ts is passed, the token will
        be refreshed. A lock is used to prevent refreshing the token twice.

        :return: Access token (string)
        """
        async with self._lock:
            if self._refresh_ts < time.time():
                await self._refresh_token()
            return self._token['access_token']

    async def connect(self):
        """Connect to the google cloud. If no token file is found the user
        will be prompted to open a given link and copy/past an code. This
        usually is only required once and future access tokens will be
        received by using the refresh token.

        A lock is used to prevent connecting twice.

        :return: None
        """
        async with self._lock:
            if self._token is None:
                logging.info('Token is missing, request a new token.')
                self._token = await self._ask()
                self._save_token()
                self._update_refresh_ts()
                return

            assert self._refresh_ts is not None, \
                'When having a token we should also have a refresh_ts value.'

            if self._refresh_ts < time.time():
                await self._refresh_token()
            else:
                logging.info('Token is valid.')

    async def _refresh_token(self):
        logging.info(
            'Token has exceeded half of the expiration time, '
            'starting a token refresh.')

        data = {
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self._token['refresh_token']
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(TOKEN_URL, data=data) as resp:
                content = await resp.text()
                content = json.loads(content)
                if resp.status == 200:
                    logging.info('Authentication successful')
                    self._token.update(content)
                    self._token['timestamp'] = int(time.time())
                    self._save_token()
                    self._update_refresh_ts()
                else:
                    raise ValueError(
                        'Got an error while asking for a token '
                        'refresh: {} ({})'
                        .format(
                            content.get('error', 'unknown'),
                            resp.status
                        ))

    def _save_token(self):
        path = os.path.dirname(self._token_file)
        if path and not os.path.exists(path):
            os.mkdir(path)
        with open(self._token_file, 'w') as f:
            json.dump(self._token, f)

    async def _ask(self):
        url = '{}?{}'.format(AUTH_URL, urlencode({
            'response_type': 'code',
            'approval_prompt': 'force',
            'access_type': 'offline',
            'scope': ' '.join(self._scopes),
            'client_id': self._client_id,
            'redirect_uri': REDIRECT_URI
        }))

        while True:
            code = input('''
Open a browser, copy/paste the following link and paste the code here:
{}
code: '''.format(url))

            if not code:
                continue

            data = {
                'code': code,
                'redirect_uri': REDIRECT_URI,
                'client_id': self._client_id,
                'client_secret': self._client_secret,
                'grant_type': 'authorization_code'
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(TOKEN_URL, data=data) as resp:
                    content = await resp.text()
                    content = json.loads(content)
                    if resp.status == 200:
                        logging.info('Authentication successful')
                        content['timestamp'] = int(time.time())
                        content['scopes'] = list(self._scopes)
                        return content

                    print('Got an error: {} ({})'.format(
                        content.get('error', 'unknown'),
                        resp.status
                    ))
