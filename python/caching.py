import json
import os
import uuid

# import wcl

# i know this is the wrong way to do it, but it works and there is zero intent for this to contain a large amount of data, so so fuck you
# i also just am not doing anything in place. hell no. i'll just rewrite the entire index any time i modify it

cache_index = '../cache/index.json'


class Cache:

    def __init__(self, identifier):
        # load or initialize cache
        try:
            self.cache = read_artifact(cache_index)
        except IOError:
            initialize_cache()
            self.cache = read_artifact(cache_index)
        self.identifier = identifier
        self.uuid = self.lookup_uuid()
        if self.uuid is not None:
            # print('a')
            self.path = self.generate_path()
            # print(self.path)
            self.data = read_artifact(self.path)
        else:
            # print('b')
            self.uuid = uuid.uuid4()
            self.path = self.generate_path()
            self.data = None

    def lookup_uuid(self):
        for entry in self.cache:
            if entry['identifier'] == self.identifier:
                return entry['uuid']
        return None

    def generate_path(self):
        return '../cache/' + self.identifier['reportCode'] + '/' + str(self.uuid) + '.json'

    def write_to_cache(self, data):
        self.data = data
        self.cache.append({'identifier': self.identifier, 'uuid': str(self.uuid)})
        write_artifact(self.cache, cache_index)
        write_artifact(data, self.path)


def initialize_cache():
    init = []
    write_artifact(init, cache_index)


def read_artifact(path):
    with open(path, 'r') as openfile:
        json_object = json.load(openfile)
    # print(json_object)
    return json_object


def write_artifact(artifact, path):
    json_object = json.dumps(artifact, indent=2)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as outfile:
        outfile.write(json_object)
    return 0


def build_identifier(data):
    return data | {'uuid': uuid.uuid4()}


# def generate_path(identifier):
#     return identifier['reportCode']+identifier['uuid']+'.json'

# def check_cache_for_artifact(identifier):
#     try:
#         index = read_artifact(cache_index)
#     except:
#         initialize_cache()
#         return check_cache_for_artifact(identifier)
#     for k in index:
#         if (k == identifier):
#             return True
#     return False

# def buildIdentifier(reportCode, startTime, endTime, id, abilityID, dataType):
#     temp = {'reportCode': reportCode, 'startTime': startTime, 'endTime': endTime, 'id': id, 'abilityID': abilityID, 'dataType': dataType}
#     temp['path'] = buildArtifactPath(temp)
#     return temp

# def buildArtifactPath(identifier):
#     return 'cache/' + identifier['reportCode'] + '/' + str(identifier['startTime']) + '-' + str(identifier['endTime']) + '_' + str(identifier['id']) + '_' + str(identifier['abilityID']) + '_' + identifier['dataType'] + '.json'

# def addArtifactToCache(artifact, identifier):
#     cache = readArtifact(cacheIndex)
#     cache.append(identifier)
#     dumpArtifact(cache, cacheIndex)
#     dumpArtifact(artifact, identifier)
#     return 0

# def cachedReturnQuery(reportCode, startTime, endTime, id, abilityID, dataType, fields, p=None, override=None):
#     identifier = buildIdentifier(reportCode, startTime, endTime, id, abilityID, dataType)
#     if (checkCacheForArtifact(identifier)):
#         print('Artifact exists in cache.')
#         return readArtifact(identifier)
#     eventSlice = wcl.completeEvent(startTime, endTime, id, abilityID, dataType)
#     if override:
#         eventSlice = override
#     artifact = wcl.returnQuery(reportCode, eventSlice, fields, p)
#     addArtifactToCache(artifact, identifier)
#     return artifact
