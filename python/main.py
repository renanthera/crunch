import wcl
import wcl_n
import math
import time

import Stagger

from itertools import chain

def fmt(v):
    vals = 'kmbt'
    digits = math.floor(math.log10(v))
    index = math.floor(digits / 3)
    if (index > 0):
        return f'{round(v / 10 ** ( index * 3), 1)}{vals[index - 1]}'
    return f'{round(v, 1)}'


def t(ms):
    seconds = ms / 1000
    minutes = math.floor(seconds / 60)
    hours = math.floor(minutes / 60)
    remainder = seconds - 60 * (minutes + 60 * hours)
    sec = math.floor(remainder)
    dec = str(round(remainder - sec, 3))[2:]
    return '{hours:0=2}:{minutes:0=2}:{sec:0=2}.{dec:0<3}'.format(hours=hours, minutes=minutes, dec=dec, sec=sec)

def p(d):
    for e in d.data:
        print(e)

wcl.pointsSpent()

# report code
reportCode = '7xNnGhDMK19vtVYF'

# gather segments to input start and end time
p(wcl_n.getSegments(reportCode))

# Valdrakken Dummies (CASE 1)
startTime = 34
endTime = 317258

# Turnip Target Dummy in Africa w/o Catue + Niuzao (CASE 2)
startTime = 1279095
endTime = 1573769

# Turnip Target Dummy in Africa w/ Catue + Niuzao (CASE 3)
startTime = 10116755
endTime = 10416126


# gather player info to enter player id
# p(wcl_n.getPlayerInfo(reportCode, startTime, endTime))
# p(wcl_n.getMasterData(reportCode))

# sometimes neither work, and you just have to get it from the UI?
id = str(20)

# assert(False)

# gather segment data for player
# healing      = wcl_n.getEvents(reportCode, None, {'dataType':'Healing',     'targetID':id, 'sourceID':id,      'translate':'true',    'startTime':startTime, 'endTime':endTime, 'useAbilityIDs':'true'})
# buffs        = wcl_n.getEvents(reportCode, None, {'dataType':'Buffs',       'targetID':id, 'sourceID':id,      'translate':'true',    'startTime':startTime, 'endTime':endTime, 'useAbilityIDs':'true'})
# casts        = wcl_n.getEvents(reportCode, None, {'dataType':'Casts',       'sourceID':id, 'translate':'true', 'startTime':startTime, 'endTime':endTime,     'useAbilityIDs':'true'})
# damage_taken = wcl_n.getEvents(reportCode, None, {'dataType':'DamageTaken', 'sourceID':id, 'translate':'true', 'startTime':startTime, 'endTime':endTime,     'useAbilityIDs':'true'})

charred_dreams                 = wcl_n.getEvents(reportCode, None, {'dataType': 'DamageDone', 'abilityID': 425299, 'startTime': startTime, 'endTime': endTime, 'useAbilityIDs': 'true', 'sourceID': id})
shadowflame_wreathe            = wcl_n.getEvents(reportCode, None, {'dataType': 'DamageDone', 'abilityID': 406764, 'startTime': startTime, 'endTime': endTime, 'useAbilityIDs': 'true', 'sourceID': id})
# elementium_pocket_anvil      = wcl_n.getEvents(reportCode, None, {'dataType': 'DamageDone', 'abilityID': 425299, 'startTime': startTime, 'endTime': endTime, 'useAbilityIDs': 'true', 'sourceID': id})
celestial_brew                 = wcl_n.getEvents(reportCode, None, {'dataType': 'Buffs', 'abilityID':      425965, 'startTime': startTime, 'endTime': endTime, 'useAbilityIDs': 'true', 'sourceID': id})
charred_dreams_data            = list(chain.from_iterable(charred_dreams.data))
shadowflame_wreathe_data       = list(chain.from_iterable(shadowflame_wreathe.data))
# elementium_pocket_anvil_data = list(chain.from_iterable(elementium_pocket_anvil.data))
celestial_brew_data            = list(chain.from_iterable(celestial_brew.data))

# flatten data
# healing_data      = list(chain.from_iterable(healing.data))
# buffs_data        = list(chain.from_iterable(buffs.data))
# casts_data        = list(chain.from_iterable(casts.data))
# damage_taken_data = list(chain.from_iterable(damage_taken.data))

# merge data and sort by timestamp
data = sorted(
    # healing_data + buffs_data + casts_data + damage_taken_data,
    # healing_data,
    charred_dreams_data + celestial_brew_data + shadowflame_wreathe_data, # + elementium_pocket_anvil_data,
    key=lambda s: (s.get('timestamp')))

acc = 0
amt = 0
ct = 0
for k in data:
    spell_id = k.get('abilityGameID')
    if spell_id == 425299:
        amt += k.get('unmitigatedAmount')
        # print(k.get('sourceID'), k.get('targetID'))
        # amt += k.get('amount')
    # if spell_id == 425965 and k.get('type') == 'removebuff':
    #     print(k)
    #     amt = 0
    if spell_id == 425965 and k.get('type') == 'applybuff':
        absorb = k.get('absorb')
        reverse_crit_vers = absorb / (1 + 0.8 * 0.4007) / (1 + 0.2165)
        acc += absorb
        ct += 1
        print('Absorb:', k.get('absorb'))
        print('Damage Dealt since last:', amt)
        print('Difference:', amt - absorb)
        # print('Reverse crit and vers:', reverse_crit_vers)
        if amt > 0:
            print('Ratio:', absorb / amt)
            print('Inverse ratio:', amt / absorb)
        # print('Reverse Ratio:', reverse_crit_vers / amt)
        print()
        amt = 0

print(acc / ct)

# total = 0
# ids_map = {}
# for e in data:
#     if e.get('abilityGameID') == 414143 and e.get('type') == 'absorbed':
#         total += e.get('amount')
#         ids_map[e.get('extraAbilityGameID')] = ids_map.get(e.get('extraAbilityGameID'), 0) + e.get('amount')

# print(ids_map)
# print(total)

# sort = {k: v for k, v in sorted(ids_map.items(), key=lambda item: -1 * item[1])}

# print('spell id, amount, percent')
# for k, v in sort.items():
#     print(k, fmt(v), f'{round(v/total*100, 2)}%')


# st = Stagger.Stagger(data)
# st.process()
# print(st.types)
# print(st.hit_types)

# for e in healing.data:
#     for f in e:
#         print(f)

# for e in u.data:
#     print(e)
# for e in v.data:
#     print(e)

# # this needs defucking after rewrite
# # startTime, endTime, id = wcl.executeMenus(reportCode, encounterIDBlacklist)

# # healing events targeting player
# dataType = 'Healing'
# events = {
#     'translate': 'false',
#     'startTime': startTime,
#     'endTime': endTime,
#     'useAbilityIDs': 'true',
#     'targetID': id,
#     'sourceID': id,
#     'dataType': dataType
# }
# # heals = wcl.Events(events, reportCode)
# # print(wcl.completeQuery(reportCode, heals.query()))

# y = wcl_n.Events(reportCode, events, 'data nextPageTimestamp')
# z = wcl_n.Request(y)

# # goto: 124907, 178173
# # expel harm: 322101
# ids = [124507, 178173, 322101]
# blacklist = ['buffs', 'sourceID', 'fight', 'targetID', 'tick', 'type']

# def process(arr):
#     sum = 0
#     ct = 0
#     for event in arr:
#         ct += 1
#         heal = event.get('amount')
#         overheal = event.get('overheal')
#         if heal is None:
#             heal = 0
#         if overheal is None:
#             overheal = 0
#         if event.get('hitType') == 2:
#             sum += (heal + overheal) / 2
#         else:
#             sum += (heal + overheal)
#     return sum / ct

# eh = []
# for k in z.data:
#     if k.get('abilityGameID') == 322101:
#         eh.append(k.get('timestamp'))

# ehgoto = []
# nonehgoto = []

# for k in z.data:
#     if k.get('abilityGameID') in ids:
#         if k.get('timestamp') in eh and k.get('abilityGameID') != 322101:
#             ehgoto.append(k)
#         if k.get('timestamp') not in eh and k.get('abilityGameID') != 322101:
#             nonehgoto.append(k)
#         for u,v in k.items():
#             if u not in blacklist and u != 'timestamp':
#                 print(u, v, end=' ')
#             if u not in blacklist and u == 'timestamp':
#                 print(t(v-startTime), end=' - ')
#         if k.get('abilityGameID') == 322101:
#             print('---------',end='')
#         print()

# ehavg = process(ehgoto)
# nonehavg = process(nonehgoto)
# print(ehavg / nonehavg, ehavg, nonehavg)

# # # damage events targeting player
# # dataType = 'DamageTaken'
# # events = {'translate': 'false', 'startTime': startTime, 'endTime': endTime, 'useAbilityIDs': 'true', 'sourceID': id, 'dataType': dataType}
# # damage = wcl.Events(events, reportCode)

# # # buffs
# # dataType = 'Buffs'
# # events = {'translate': 'false', 'startTime': startTime, 'endTime': endTime, 'useAbilityIDs': 'true', 'targetID': id, 'sourceID': id, 'dataType': dataType}
# # buffs = wcl.Events(events, reportCode)

# # filteredbuffs = []
# # for k in buffs.data:
# #     if k.get('abilityGameID') == 195630 and k.get('type') != 'refreshbuff':
# #         filteredbuffs.append(k)
# #         # print(t(k['timestamp']-startTime), k)

# # prev_timestamp = 0
# # tmp = []
# # index = 0
# # # print(filteredbuffs[l])
# # for k in damage.data:
# #     if k.get('targetID') == int(id) and k.get('abilityGameID') <= 1:
# #         if k['timestamp'] != prev_timestamp:
# #             if len(tmp) > 1:
# #                 while filteredbuffs[index]['timestamp'] < prev_timestamp:
# #                     index += 1
# #                 index -= 1
# #                 match filteredbuffs[index].get('type'):
# #                     case 'applybuff':
# #                         count = 1
# #                     case 'applybuffstack':
# #                         count = filteredbuffs[index].get('stack')
# #                     case 'removebuff':
# #                         count = 0
# #                     case _:
# #                         count = -1
# #                 print(count)
# #                 for l in tmp[:]:
# #                     print(t(l['timestamp'] - startTime), l['hitType'])
# #                 print()
# #             tmp = []
# #         tmp.append(k)
# #         prev_timestamp = k['timestamp']

# # hitType:
# # 0 -> miss
# # 1 -> hit
# # 7 -> dodge
# # 8 -> parry

# # when melees are synced, are all hits tested against the same dodge chance?

# # things to identify:
# # current base dodge
# # current mastery
# # current eb stacks
# # is the player doing something that prevents dodges during this event (skip all sets with 0 dodges?)

# # s = []
# # for k in heals.data:
# #     if k['type'] == 'heal':
# #         s.append({'timestamp': k['timestamp'], 'niceTime': castMS(k['timestamp'] - startTime, 3), 'size': k.get('amount', 0) + k.get('overheal', 0), 'event': 'h'})
# # for k in damage.data:
# #     s.append({'timestamp': k['timestamp'], 'niceTime': castMS(k['timestamp'] - startTime, 3), 'size': k.get('amount', 0) + k.get('absorbed', 0), 'event': 'd'})
# # for k in absorb.data:
# #     if 'absorb' in k:
# #         if k['absorb'] != 0:
# #             s.append({'timestamp': k['timestamp'], 'niceTime': castMS(k['timestamp'] - startTime, 3), 'size': k.get('absorb', 0), 'event': 'a'})
# # s = sorted(s, key=lambda x: x['timestamp'])
# # for r in s:
# #     print(r['timestamp'],'\t',r['event'],'\t',r)

# # wcl.pointsSpent()
