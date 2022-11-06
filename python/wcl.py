import requests
import json
import pickle
from requests.exceptions import HTTPError
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from tabulate import tabulate

tokenURI = 'https://www.warcraftlogs.com/oauth/token'
v2endpoint = 'https://www.warcraftlogs.com/api/v2/client'

tokenFilename = 'token.tk'
credentialsFilename = 'credentials'


def recurseJson(O, S):
  try:
    if (len(S) == 1):
      return O[S[0]]
    return recurseJson(O[S[0]], S[1:])
  except:
    print(O)


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
    return request
  except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}')
    raise SystemExit


def completeQuery(code, query):
  return '{reportData{report(code:"' + code + '"){' + query + '}}}'


def completeEvent(startTime, endTime, id, abilityID, dataType):
  return 'events(translate:false startTime:' + str(startTime) + ' endTime:' + str(endTime) + 'useAbilityIDs:true sourceID:' + id + ' abilityID:' + abilityID + ' dataType:' + dataType + '){data nextPageTimestamp}'


def returnQuery(code, query, fields=None, p=None):
  query = completeQuery(code, query)
  request = getRequest(query)
  requestJson = json.loads(request.text)
  if (filter != None):
    requestJson = recurseJson(requestJson, fields)
  if (p != None):
    print(json.dumps(requestJson, indent=2))
  return requestJson


def pointsSpent():
  pointsSpentThisHour = "{ rateLimitData { pointsSpentThisHour } }"
  request = getRequest(pointsSpentThisHour)
  requestJson = json.loads(request.text)
  fields = ['data', 'rateLimitData', 'pointsSpentThisHour']
  print('points spent: ' + str(recurseJson(requestJson, fields)) + '/3600')


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


def dumpArtifact(artifact, name):
  json_object = json.dumps(artifact, indent=2)
  with open(name + ".json", "w") as outfile:
    outfile.write(json_object)
