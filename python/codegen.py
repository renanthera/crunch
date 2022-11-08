import caching
import json



def resolveTypes(types):
    main = {}
    for k in types['data']['__schema']['types']:
        if (k['kind'].lower() == 'object'):
            main[k['name'].lower()] = [z['name'].lower() for z in k['fields']]
        if (k['kind'].lower() == 'enum'):
            main[k['name'].lower()] = [z['name'].lower() for z in k['enumValues']]
        if (k['kind'].lower() == 'scalar'):
            main[k['name'].lower()] = None
    return main


def processEntry(v):
    if (type(v) is not list and type(v) is not dict):
        return v
    else:
        return trimEntry(v)


def trimEntry(entry):
    blacklist = ['includeDeprecated', 'isDeprecated', 'deprecationReason']
    out = {}
    if (type(entry) is dict):
        if (entry['name'] not in blacklist):
            for k, v in entry.items():
                if (k not in blacklist):
                    if (v is not None and v != [] and v != {}):
                        out[k] = processEntry(v)
    elif (type(entry) is list):
        for k in entry:
            if (k is not None and k != [] and k != {}):
                if (k['name'] not in blacklist):
                    out[k['name']] = processEntry(k)
    return out


def processEntries(group):
    obj = {}
    obj['kind'] = group['kind']
    obj['name'] = group['name']
    if (group['fields'] is not None):
        for subentry in group['fields']:
            if ('name' in subentry):
                obj[subentry['name']] = trimEntry(subentry)
            elif ('kind' in entry):
                obj[subentry['kind']] = trimEntry(subentry)
    elif (group['enumValues'] is not None):
        for subentry in group['enumValues']:
            if ('name' in subentry):
                obj[subentry['name']] = trimEntry(subentry)
            elif ('kind' in entry):
                obj[subentry['kind']] = trimEntry(subentry)
    else:
        return group
    return obj


def postProcess(obj):
    out = {}
    if (type(obj) is dict):
        for k, v in obj.items():
            if (v != {} and type(v) is not dict):
                out[k] = v
            elif (v != {} and type(v) is dict):
                out[k] = postProcess(v)
    return out


def populateTypes(schema):
    for entry in schema['data']['__schema']['types'][:]:
        print(entry['name'], '{')
        data = postProcess(processEntries(entry))
        for k, v in data.items():
            print(k, v)
        print('}\n')


# populateTypes(schema)


# def trimSchema(schema):
#     blacklist = ['includeDeprecated', 'isDeprecated', 'deprecationReason', [], {}]
#     if (type(schema) is dict):
#         for k, v in schema.items():
#             if (v in blacklist):
#                 schema.pop(k)
#             elif (type(v) is dict or type(v) is list):
#                 trimSchema(v)
#     elif (type(schema) is list):
#         for k in schema:
#             if (k in blacklist):
#                 schema.remove(k)
#             elif (type(k) is dict or type(k) is list):
#                 trimSchema(k)


# schema = caching.readArtifact({'path': 'cache/schema.json'})
# trimSchema(schema)
# dumpArtifact(schema, {'path': 'python/temp'})

def jsonhook(dct):
    blacklistk = ['includeDeprecated', 'isDeprecated', 'deprecationReason']
    blacklistv = [[],{},None]
    o = {}
    for k, v in dct.items():
        if k not in blacklistk and v not in blacklistv:
            if type(v) is str:
                o[k.lower()] = v.lower()
            else:
                o[k.lower()] = v
    return o


with open('../cache/schema.json', 'r') as openfile:
    schema = json.load(openfile,object_hook=jsonhook)

output = json.dumps(schema, indent=2)
with open('temp', 'w') as outfile:
    outfile.write(output)

# generate all fields from schema, strictly from __name fields
# __schema -> types
# __type -> type members
# __typekind -> types + type overloads
# __field -> type field members
# __inputvalue -> ???
# __enumvalue -> magic strings for constant, finite type descriptions
# __directive -> ???
# __directivelocation -> ???
