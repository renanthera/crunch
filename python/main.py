import wcl
import wcl_n
import math
import time


def t(ms):
    seconds = ms / 1000
    minutes = math.floor(seconds / 60)
    hours = math.floor(minutes / 60)
    remainder = seconds - 60 * (minutes + 60 * hours)
    sec = math.floor(remainder)
    dec = str(round(remainder - sec, 3))[2:]
    return '{hours:0=2}:{minutes:0=2}:{sec:0=2}.{dec:0<3}'.format(hours=hours, minutes=minutes, dec=dec, sec=sec)


startTime = 106299762
endTime = 108067141
id = str(250)

reportCode = 'rjkMQZYz6ALWnv21'
encounterIDBlacklist = []

# tok = wcl_n.Token()

# this needs defucking after rewrite
# startTime, endTime, id = wcl.executeMenus(reportCode, encounterIDBlacklist)

# healing events targeting player
dataType = 'Healing'
events = {'translate': 'false', 'startTime': startTime, 'endTime': endTime, 'useAbilityIDs': 'true', 'targetID': id, 'dataType': dataType}
heals = wcl.Events(events, reportCode)
print(wcl.completeQuery(reportCode, heals.query()))

# test = {
#     'reportData': {
#         'arguments': None,
#         'query': {
#             'report': {
#                 'arguments': {'code': reportCode},
#                 'query': {
#                     'events': {
#                         'arguments': {'translate': 'false', 'startTime': startTime, 'endTime': endTime, 'useAbilityIDs': 'true', 'targetID': id, 'dataType': dataType},
#                         'query': {'data', 'nextPageTimestamp'}
#                     }
#                 }
#             }
#         }
#     }
# }

# b = {'data','nextPageTimestamp'}
# print(b)
# for k in b:
#     print(k)

# # damage events targeting player
# dataType = 'DamageTaken'
# events = {'translate': 'false', 'startTime': startTime, 'endTime': endTime, 'useAbilityIDs': 'true', 'sourceID': id, 'dataType': dataType}
# damage = wcl.Events(events, reportCode)

# # buffs
# dataType = 'Buffs'
# events = {'translate': 'false', 'startTime': startTime, 'endTime': endTime, 'useAbilityIDs': 'true', 'targetID': id, 'sourceID': id, 'dataType': dataType}
# buffs = wcl.Events(events, reportCode)

# filteredbuffs = []
# for k in buffs.data:
#     if k.get('abilityGameID') == 195630 and k.get('type') != 'refreshbuff':
#         filteredbuffs.append(k)
#         # print(t(k['timestamp']-startTime), k)

# prev_timestamp = 0
# tmp = []
# index = 0
# # print(filteredbuffs[l])
# for k in damage.data:
#     if k.get('targetID') == int(id) and k.get('abilityGameID') <= 1:
#         if k['timestamp'] != prev_timestamp:
#             if len(tmp) > 1:
#                 while filteredbuffs[index]['timestamp'] < prev_timestamp:
#                     index += 1
#                 index -= 1
#                 match filteredbuffs[index].get('type'):
#                     case 'applybuff':
#                         count = 1
#                     case 'applybuffstack':
#                         count = filteredbuffs[index].get('stack')
#                     case 'removebuff':
#                         count = 0
#                     case _:
#                         count = -1
#                 print(count)
#                 for l in tmp[:]:
#                     print(t(l['timestamp'] - startTime), l['hitType'])
#                 print()
#             tmp = []
#         tmp.append(k)
#         prev_timestamp = k['timestamp']

# hitType:
# 0 -> miss
# 1 -> hit
# 7 -> dodge
# 8 -> parry

# when melees are synced, are all hits tested against the same dodge chance?

# things to identify:
# current base dodge
# current mastery
# current eb stacks
# is the player doing something that prevents dodges during this event (skip all sets with 0 dodges?)

# s = []
# for k in heals.data:
#     if k['type'] == 'heal':
#         s.append({'timestamp': k['timestamp'], 'niceTime': castMS(k['timestamp'] - startTime, 3), 'size': k.get('amount', 0) + k.get('overheal', 0), 'event': 'h'})
# for k in damage.data:
#     s.append({'timestamp': k['timestamp'], 'niceTime': castMS(k['timestamp'] - startTime, 3), 'size': k.get('amount', 0) + k.get('absorbed', 0), 'event': 'd'})
# for k in absorb.data:
#     if 'absorb' in k:
#         if k['absorb'] != 0:
#             s.append({'timestamp': k['timestamp'], 'niceTime': castMS(k['timestamp'] - startTime, 3), 'size': k.get('absorb', 0), 'event': 'a'})
# s = sorted(s, key=lambda x: x['timestamp'])
# for r in s:
#     print(r['timestamp'],'\t',r['event'],'\t',r)

# wcl.pointsSpent()
