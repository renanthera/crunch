import json
import os

import wcl

# i know this is the wrong way to do it, but it works and there is zero intent for this to contain a large amount of data, so so fuck you
# i also just am not doing anything in place. hell no. i'll just rewrite the entire index any time i modify it

cacheIndex = {'path': 'cache/index.json'}


def initCache():
    init = []
    os.makedirs(os.path.dirname('../' + cacheIndex['path']), exist_ok=True)
    dumpArtifact(init, cacheIndex)


def buildIdentifier(reportCode, startTime, endTime, id, abilityID, dataType):
    temp = {'reportCode': reportCode, 'startTime': startTime, 'endTime': endTime, 'id': id, 'abilityID': abilityID, 'dataType': dataType}
    temp['path'] = buildArtifactPath(temp)
    return temp


def buildArtifactPath(identifier):
    return 'cache/' + identifier['reportCode'] + '/' + str(identifier['startTime']) + '-' + str(identifier['endTime']) + '_' + str(identifier['id']) + '_' + str(identifier['abilityID']) + '_' + identifier['dataType'] + '.json'


def checkCacheForArtifact(identifier):
    try:
        index = readArtifact(cacheIndex)
    except:
        initCache()
        return checkCacheForArtifact(identifier)
    for k in index:
        if (k == identifier):
            return True
    return False


def addArtifactToCache(artifact, identifier):
    cache = readArtifact(cacheIndex)
    cache.append(identifier)
    dumpArtifact(cache, cacheIndex)
    dumpArtifact(artifact, identifier)
    return 0


def readArtifact(identifier):
    with open('../' + identifier['path'], 'r') as openfile:
        json_object = json.load(openfile)
    return json_object


def dumpArtifact(artifact, identifier):
    json_object = json.dumps(artifact, indent=2)
    os.makedirs(os.path.dirname('../' + identifier['path']), exist_ok=True)
    with open('../' + identifier['path'], "w") as outfile:
        outfile.write(json_object)
    return 0


def cachedReturnQuery(reportCode, startTime, endTime, id, abilityID, dataType, fields, p=None):
    identifier = buildIdentifier(reportCode, startTime, endTime, id, abilityID, dataType)
    if (checkCacheForArtifact(identifier)):
        print('Artifact exists in cache.')
        return readArtifact(identifier)
    eventSlice = wcl.completeEvent(startTime, endTime, id, abilityID, dataType)
    artifact = wcl.returnQuery(reportCode, eventSlice, fields, p)
    addArtifactToCache(artifact, identifier)
    return artifact
