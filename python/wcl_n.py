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
    prefix = ''
    kind = ''
    suffix = ''

    def __init__(self, args, fields):
        self.args = args
        self.fields = fields
        self.query = self.stringify()

    def stringify(self):
        if (self.args is None):
            query = self.prefix + self.kind
        else:
            query = self.prefix + self.kind + '('

        if isinstance(self.args, str):
            query += self.args + ' '
        elif isinstance(self.args, dict):
            for key, value in self.args.items():
                if value is not None:
                    query += key + ':' + str(value) + ' '
        elif isinstance(self.args, set):
            for value in self.args.items():
                query += value + ' '

        if (self.args is None):
            query = query + '{'
        else:
            query = query[:-1] + '){'

        if isinstance(self.fields, str):
            query += self.fields + ' '
        elif isinstance(self.fields, dict):
            for key, value in self.fields.items():
                if value is not None:
                    query += key + ':' + str(value) + ' '
        elif isinstance(self.fields, set):
            for value in self.fields:
                query += value + ' '
        query = query[:-1] + '}' + self.suffix

        return query

    def update_query(self, args=None, fields=None):
        if args is not None:
            for key, value in args.items():
                self.args.update({key: value})
        if fields is not None:
            for key, value in fields.items():
                self.fields.update({key: value})
        self.query = self.stringify()


class Events(Query):

    def __init__(self, reportCode, args, fields):
        self.cache = True
        self.prefix = '{reportData{report(code:"' + reportCode + '"){'
        self.kind = 'events'
        self.suffix = '}}}'
        if (fields is None):
            fields = 'data nextPageTimestamp'
        super().__init__(args, fields)

class ReportInfo(Query):
    def __init__(self, reportCode):
        self.cache = False
        fields = 'id encounterID name difficulty  kill startTime endTime'
        self.prefix = '{reportData{report(code:"' + reportCode + '"){'
        self.kind = 'fights'
        self.suffix = '}}}'
        super().__init__(None, fields)

class PlayerInfo(Query):
    def __init__(self, reportCode, startTime, endTime):
        args = {
            'translate': 'false',
            'startTime': startTime,
            'endTime': endTime,
        }
        self.cache = False
        self.prefix = '{reportData{report(code:"' + reportCode + '"){'
        self.kind = 'playerDetails'
        self.suffix = '}}'
        super().__init__(args, None)

class MasterData(Query):
    def __init__(self, reportCode):
        args = {
            'translate': 'false'
        }
        fields = 'actors{id name type subType gameID}'
        self.cache = False
        self.prefix = '{reportData{report(code:"' + reportCode + '"){'
        self.kind = 'masterData'
        self.suffix = '}}}'
        super().__init__(args, fields)



class Request:
    v2endpoint = 'https://www.warcraftlogs.com/api/v2/client'

    def __init__(self, query):
        self.token = Token()
        self.query = query
        self.data = []
        if self.query.cache:
            self.cache = caching.Cache(self.query.query)
            if self.cache.data is not None:
                print('reading', self.query.query, 'from cache')
                self.data = self.cache.data
                return
        self.get_entire_request()
        if self.query.cache:
            self.cache.write_to_cache(self.data)
        return

    def get_entire_request(self):
        body = self.get_request()

        # i hate this solution, but i don't have any idea how to come up with something better right now
        try:
            payload = body['data']['reportData']['report'][self.query.kind]
        except:
            print('failed:')
            print(body)
            return
        if isinstance(payload, dict):
            self.data.append(payload.get('data'))
            if payload.get('nextPageTimestamp'):
                self.query.update_query({'startTime': payload.get('nextPageTimestamp')})
                self.get_entire_request()
                return
            return
        else:
            self.data = payload
        return

    def get_request(self, failed=0):
        print('requesting', self.query.query)
        try:
            request = requests.post(self.v2endpoint, headers={'Authorization': "Bearer " + self.token.token['access_token']}, data={'query': self.query.query})
            if (request.text == "{\"error\":\"Unauthenticated.\"}"):
                if (failed == 1):
                    print('Already failed once. Something\'s borked, fix it yourself.')
                    return -1
                print('Unauthenticated. Attempting to obtain new token and re-run query.')
                self.token.get()
                return self.get_request(failed=1)
            return json.loads(request.text)
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise SystemExit

def getSegments(reportCode):
    return Request(ReportInfo(reportCode))

def getPlayerInfo(reportCode, startTime, endTime):
    return Request(PlayerInfo(reportCode, startTime, endTime))

def getMasterData(reportCode):
    return Request(MasterData(reportCode))

def getEvents(reportCode, fields, args):
    return Request(Events(reportCode, args, fields))

def printPlayerInfo(reportCode, startTime, endTime):
    req = getPlayerInfo(reportCode, startTime, endTime)
    for entry in req.data:
        players = entry.get('playerDetails')
        for role, player_list in players.items():
            print('  ', role)
            for player in player_list:
                print(
                    '    ',
                    player.get('id'),
                    player.get('name'),
                    player.get('type'),
                    player.get('specs'),
                )
