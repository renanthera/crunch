import json


def jsonhook(dct):
    blacklistk = ['includeDeprecated', 'isDeprecated', 'deprecationReason']
    blacklistv = [[], {}, None]
    o = {}
    for k, v in dct.items():
        if k not in blacklistk and v not in blacklistv:
            if type(v) is str:
                o[k.lower()] = v.lower()
            else:
                o[k.lower()] = v
    return o


schemapath = '../cache/schema.json'
# with open(schemapath, 'r') as openfile:
#     schema = json.load(openfile, object_hook=jsonhook)

# output = json.dumps(schema, indent=2)
# with open('temp', 'w') as outfile:
#     outfile.write(output)

temppath = 'temp'
with open(temppath, 'r') as openfile:
    schema = json.load(openfile)

types = schema['data']['__schema']['types']


def objectNames(type):
    if type['kind'] == 'object':
        return 'struct '
    elif type['kind'] == 'enum':
        return 'enum '
    elif type['kind'] == 'scalar':
        return '// scalar ' + type['name'] + '\n'

def scalarResolver(k):
    name = k['name']
    if name == 'boolean':
        return 'bool'
    elif name == 'int':
        return 'int'
    elif name == 'string':
        return 'std::string'
    elif name == 'float':
        return 'float'
    elif name == 'json':
        return '// json'
    return "scalar!!!!!!!"


def typeResolver(k):
    # not oftype
    if 'type' in k:
        r = k['type']
    # oftype
    else:
        r = k
    if 'kind' not in r:
        return ''
    match r['kind']:
        case 'scalar':
            return scalarResolver(r)
        case 'object':
            return r['name']
        case 'interface':
            return '!!!!!interface'
        case 'union':
            return '!!!!!union'
        case 'enum':
            return 'int'
        case 'input_object':
            return '!!!!!input_object'
        case 'list':
            return typeResolver(r['oftype'])+'*'
        case 'non_null':
            return typeResolver(r['oftype'])
        case _:
            return "!!!unknown type"

def nameResolver(k):
    if 'type' in k:
        if 'kind' in k['type']:
            if k['type']['kind'] == 'enum':
                return k['type']['name']
    return k['name']

objects = []
members = []
validmembers = ['object','interface','union','enum','input_object','list','non_null']

tabs = 0
tab = "  "
print(tabs * "  " + "namespace types {")
tabs += 1
for type in types:
    print()
    print(tabs * tab + objectNames(type), end='')
    if objectNames(type) == '// scalar ' + type['name'] + '\n':
        continue
    print(type['name'], "{")
    tabs += 1
    if type['name'] not in objects:
        objects.append(type['name'])
    if type['kind'] != 'enum':
        for k in type['fields']:
            # print(k)
            print(tabs*tab+typeResolver(k)+'* '+nameResolver(k))
            if k['name'] not in members and k['type'] in validmembers:
                members.append(k['name'])
    else:
        for k in type['enumvalues']:
            # print(k)
            print(tabs*tab+typeResolver(k)+nameResolver(k))
    tabs -= 1
    print(tabs * tab + "};")
tabs -= 1
print(tabs * tab + "};")

for k in members:
    if k not in objects:
        print(k,' is not in objects!')

print(len(objects))
