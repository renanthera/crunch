import wcl
import math


def castMS(time, r):
    seconds = time / 1000
    minutes = math.floor(seconds / 60)
    hours = math.floor(minutes / 60)
    oseconds = seconds - 60 * (minutes + 60 * hours)
    return str(hours) + ':' + str(minutes) + ':' + str(oseconds)


startTime = 106299762
endTime = 108067141
id = str(250)

reportCode = 'rjkMQZYz6ALWnv21'
encounterIDBlacklist = []

# this needs defucking after rewrite
# startTime, endTime, id = wcl.executeMenus(reportCode, encounterIDBlacklist)

# healing events targeting player
dataType = 'Healing'
events = {'translate': 'false', 'startTime': startTime, 'endTime': endTime, 'useAbilityIDs': 'true', 'targetID': id, 'dataType': dataType}
heals = wcl.Events(events, reportCode)

# # damage events targeting player
dataType = 'DamageTaken'
events = {'translate': 'false', 'startTime': startTime, 'endTime': endTime, 'useAbilityIDs': 'true', 'targetID': id, 'dataType': dataType}
damage = wcl.Events(events, reportCode)

# # absorb buffs
dataType = 'Buffs'
events = {'translate': 'false', 'startTime': startTime, 'endTime': endTime, 'useAbilityIDs': 'true', 'targetID': id, 'dataType': dataType}
absorb = wcl.Events(events, reportCode)

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

wcl.pointsSpent()
