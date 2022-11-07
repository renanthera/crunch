import caching

schema = caching.readArtifact({'path': 'cache/schema.json'})


def recursivePrint(obj):
    if (type(obj) is dict or type(obj) is list):
        p = 0
        print()
        if (type(obj) is dict):
            if ('fields' in obj):
                if (obj['fields'] is None):
                    p = 1
        for key, value in obj.items():
            if (type(value) is dict):
                if (p == 1):
                    print(key)
                recursivePrint(value)
            elif (type(value) is list):
                if (p == 1):
                    print(key)
                for entry in value:
                    recursivePrint(entry)
            else:
                print(key, value)


# recursivePrint(schema)


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


def populateTypes(main):
    for k, v in main.items():
        arr = []
        for e in v:
            d = {'name': e, 'types': main[e]}
            arr.append(d)
        types[k] = d
    return main


types = resolveTypes(schema)

for k, v in types.items():
    print(k, v)

types = populateTypes(types)


# generate all fields from schema, strictly from __name fields
# __schema -> types
# __type -> type members
# __typekind -> types + type overloads
# __field -> type field members
# __inputvalue -> ???
# __enumvalue -> magic strings for constant, finite type descriptions
# __directive -> ???
# __directivelocation -> ???
