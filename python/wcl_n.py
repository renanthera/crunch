import requests
import json
import pickle
import caching
import time
from requests.exceptions import HTTPError
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from tabulate import tabulate


class Token:
    tokenURI = 'https://www.warcraftlogs.com/oauth/token'

    tokenFilename = 'token.tk'
    credentialsFilename = 'credentials'

    def __init__(self):
        self.token = self.read()
        # if failed to load or expiring in less than a day, acquire new token
        if (self.token is None):
            print(f'Token file missing, generating new token...')
            self.token = self.get()
        if (self.token.get('expires_at') - 3600 < time.time()):
            expiry_time = self.token.get('expires_at') - time.time()
            print(f'Token expiring in {expiry_time}, generating new token...')
            self.token = self.get()

    def read(self):
        try:
            with open(self.tokenFilename, 'rb') as handle:
                data = handle.read()
            return pickle.loads(data)
        except Exception as err:
            print(f'Failed to load token, error occurred: {err}')
            return None

    def write(self):
        file = open(self.tokenFilename, 'wb')
        pickle.dump(self.token, file)
        file.close()

    def get(self):
        try:
            clientID, clientSecret = self.loadCredentials()
            client = BackendApplicationClient(client_id=clientID)
            oauth = OAuth2Session(client=client)
            token = oauth.fetch_token(token_url=self.tokenURI, client_id=clientID, client_secret=clientSecret)
            self.write()
            return token
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise SystemExit
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise SystemExit

    def loadCredentials(self):
        with open(self.credentialsFilename, 'rb') as handle:
            data = handle.read()
        data = str(data).split('\'')
        return data[1], data[3]


class Query:
    def __init__(self):
        self.query = ''

class Request:
    v2endpoint = 'https://www.warcraftlogs.com/api/v2/client'

    def __init__(self, fields, code):
        self.token = Token()
        self.fields = fields
        self.code = code
        self.identifier = fields | {'reportCode': code} | {'OBJ': 'Events'}
        self.cache = caching.Cache(self.identifier)
        self.data = []
        if self.cache.data is not None:
            print('read', self.query(), 'from cache')
            self.data = self.cache.data
        else:
            self.get_request()
            self.cache.write_to_cache(self.data)

    def update_query(self, update):
        for key, value in update.items():
            self.fields.update({key: value})

    def query(self):
        query = 'events('
        for key, value in self.fields.items():
            if value is not None:
                query += key + ': ' + str(value) + ' '
        return query + '){data nextPageTimestamp}'

    def get_request(self):
        print('requesting', self.query())
        temp = getRequest(completeQuery(self.code, self.query()))['data']['reportData']['report']['events']
        self.data += temp.get('data')
        if temp.get('nextPageTimestamp'):
            self.update_query({'startTime': temp.get('nextPageTimestamp')})
            self.get_request()
            return
        return


def getRequest(query, failed=0):
    token = readToken()
    try:
        request = requests.post(v2endpoint, headers={'Authorization': "Bearer " + token['access_token']}, data={'query': query})
        if (request.text == "{\"error\":\"Unauthenticated.\"}"):
            if (failed == 1):
                print('Already failed once. Something\'s borked, fix it yourself.')
                return -1
            print('Unauthenticated. Attempting to obtain new token and re-run query.')
            getToken()
            return getRequest(query, failed=1)
        return json.loads(request.text)
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        raise SystemExit
