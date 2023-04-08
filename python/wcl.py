import requests
import json
import pickle
import caching
from requests.exceptions import HTTPError
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from tabulate import tabulate

tokenURI = 'https://www.warcraftlogs.com/oauth/token'
v2endpoint = 'https://www.warcraftlogs.com/api/v2/client'

tokenFilename = 'token.tk'
credentialsFilename = 'credentials'


def getToken():
    try:
        clientID, clientSecret = loadCredentials(credentialsFilename)
        client = BackendApplicationClient(client_id=clientID)
        oauth = OAuth2Session(client=client)
        token = oauth.fetch_token(token_url=tokenURI, client_id=clientID, client_secret=clientSecret)
        writeToken(token)
        return token
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        raise SystemExit
    except Exception as err:
        print(f'Other error occurred: {err}')
        raise SystemExit


def writeToken(token):
    file = open(tokenFilename, 'wb')
    pickle.dump(token, file)
    file.close()


def readToken():
    try:
        with open(tokenFilename, 'rb') as handle:
            data = handle.read()
        return pickle.loads(data)
    except:
        return getToken()


def loadCredentials(credentialsFilename):
    with open(credentialsFilename, 'rb') as handle:
        data = handle.read()
    data = str(data).split('\'')
    return data[1], data[3]


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


def pointsSpent():
    pointsSpentThisHour = "{ rateLimitData { pointsSpentThisHour } }"
    fields = ['data', 'rateLimitData', 'pointsSpentThisHour']
    request = getRequest(pointsSpentThisHour)
    print(str(request['data']['rateLimitData']['pointsSpentThisHour']) + '/3600')


# # TODO: Garbage
def completeQuery(code, query):
    return '{reportData{report(code:"' + code + '"){' + query + '}}}'


class Events:

    def __init__(self, fields, code):
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


# TODO: REDO THIS WHOLE SUBSYSTEM
def printTable(d, ti=None, tf=None):
    print(tabulate([d[i][ti:tf] for i in range(1, len(d))], headers=d[0]))


def getSegments(reportCode, encounterIDBlacklist, p=None):
    listFights = 'fights{id encounterID name difficulty kill startTime endTime}'
    fields = ['data', 'reportData', 'report', 'fights']
    segmentList = returnQuery(reportCode, listFights, fields)
    table = [['segment', 'encounter', 'difficulty', 'kill']]
    for k in segmentList:
        if (k['encounterID'] not in encounterIDBlacklist):
            table.append([k['id'], k['name'], k['difficulty'], k['kill'], k['startTime'], k['endTime']])
    if (p != None):
        printTable(table, tf=-2)
    return table


def getPlayers(reportCode, startTime, endTime, p=None):
    playerList = 'playerDetails(translate:false startTime:' + str(startTime) + ' endTime:' + str(endTime) + ')'
    fields = ['data', 'reportData', 'report', 'playerDetails', 'data', 'playerDetails']
    playerList = returnQuery(reportCode, playerList, fields)
    if (playerList == []):
        return fallbackGetPlayers(reportCode, p)
    table = [['index', 'id', 'name', 'icon']]
    for k in playerList:
        for l in playerList[k]:
            table.append([l['id'], l['name'], l['icon']])
    if (p != None):
        printTable(table)
    return table


def fallbackGetPlayers(reportCode, p=None):
    query = 'masterData(translate:false){ actors{id name type subType gameID}}'
    fields = ['data', 'reportData', 'report', 'masterData', 'actors']
    fallbackPlayerList = returnQuery(reportCode, query, fields)
    if (p != None):
        print(tabulate(fallbackPlayerList, headers='keys'))
    return fallbackPlayerList


def segmentMenu(reportCode, encounterIDBlacklist):
    segmentList = getSegments(reportCode, encounterIDBlacklist, 1)
    segmentSelection = int(input('Enter segment selection: '))
    print()
    startTime = segmentList[segmentSelection][4]
    endTime = segmentList[segmentSelection][5]
    return startTime, endTime


def playerMenu(reportCode, startTime, endTime):
    playerList = getPlayers(reportCode, startTime, endTime, 1)
    playerSelection = int(input('Enter player selection: '))
    id = str(playerSelection)
    if (type(playerSelection) == type([])):
        if (type(playerSelection[0]) == type([])):
            id = str(playerList[playerSelection][1])
    return id


def executeMenus(reportCode, encounterIDBlacklist):
    startTime, endTime = segmentMenu(reportCode, encounterIDBlacklist)
    id = playerMenu(reportCode, startTime, endTime)
    return startTime, endTime, id


# TODO: END SUBSYSTEM
