# def tier_guard_analysis( info ):
#   reportCode = info.get( 'reportCode' )
#   startTime = info.get( 'startTime' )
#   endTime = info.get( 'endTime' )
#   id = info.get( 'id' )
#   charred_dreams = wcl.getEvents(
#     reportCode,
#     None,
#     {
#       'dataType': 'DamageDone',
#       'abilityID': 425299,
#       'startTime': startTime,
#       'endTime': endTime,
#       'useAbilityIDs': 'true',
#       'sourceID': id
#     }
#   )
#   shadowflame_wreathe = wcl.getEvents(
#     reportCode,
#     None,
#     {
#       'dataType': 'DamageDone',
#       'abilityID': 406764,
#       'startTime': startTime,
#       'endTime': endTime,
#       'useAbilityIDs': 'true',
#       'sourceID': id
#     }
#   )
#   celestial_brew = wcl.getEvents(
#     reportCode,
#     None,
#     {
#       'dataType': 'Buffs',
#       'abilityID': 425965,
#       'startTime': startTime,
#       'endTime': endTime,
#       'useAbilityIDs': 'true',
#       'sourceID': id
#     }
#   )
#   charred_dreams_data = list( chain.from_iterable( charred_dreams.data ) )
#   shadowflame_wreathe_data = list( chain.from_iterable( shadowflame_wreathe.data ) )
#   celestial_brew_data = list( chain.from_iterable( celestial_brew.data ) )

#   # flatten data
#   # healing_data      = list(chain.from_iterable(healing.data))
#   # buffs_data        = list(chain.from_iterable(buffs.data))
#   # casts_data        = list(chain.from_iterable(casts.data))
#   # damage_taken_data = list(chain.from_iterable(damage_taken.data))

#   # merge data and sort by timestamp
#   data = sorted(
#       # healing_data + buffs_data + casts_data + damage_taken_data,
#       # healing_data,
#       charred_dreams_data + celestial_brew_data + shadowflame_wreathe_data, # + elementium_pocket_anvil_data,
#       key=lambda s: (s.get('timestamp')))

#   acc = 0
#   amt = 0
#   ct = 0
#   for k in data:
#     spell_id = k.get( 'abilityGameID' )
#     if spell_id == 425299:
#       amt += k.get( 'unmitigatedAmount' )
#       # print(k.get('sourceID'), k.get('targetID'))
#       # amt += k.get('amount')
#     # if spell_id == 425965 and k.get('type') == 'removebuff':
#     #     print(k)
#     #     amt = 0
#     if spell_id == 425965 and k.get( 'type' ) == 'applybuff':
#       absorb = k.get( 'absorb' )
#       reverse_crit_vers = absorb / ( 1 + 0.8 * 0.4007 ) / ( 1 + 0.2165 )
#       acc += absorb
#       ct += 1
#       # print('Absorb:', k.get('absorb'))
#       # print('Damage Dealt since last:', amt)
#       # print('Difference:', amt - absorb)
#       # print('Reverse crit and vers:', reverse_crit_vers)
#       # if amt > 0:
#       # print('Ratio:', absorb / amt)
#       # print('Inverse ratio:', amt / absorb)
#       # print('Reverse Ratio:', reverse_crit_vers / amt)
#       # print()
#       amt = 0

#   print( acc / ct )

# # runReports(tier_proc_analysis)
# # runReports(tier_guard_analysis)

# # wcl.Request(wcl.PointsSpent())
# # wcl.getPointsSpent()

# import json

import analyzers

# analyzers.ignited_essence.ignited_essence( [
#   'xrfcz1d34vjJ2LqM',
#   'ygV4kq9RLvGQ2wm8',
#   'vr1RPbDWJ9YakM8j',
# ] )

analyzers.press_the_advantage.damage( [
  'xrfcz1d34vjJ2LqM',
  'ygV4kq9RLvGQ2wm8',
  'vr1RPbDWJ9YakM8j',
] )

# analyzers.t31_brew.proc( [
#   'bkrPDQ1ZtTGRphWn',
#   'YftHvBKJzh8nxa9A',
#   'qWJXamNtPbTfZ41y',
#   '7Qct4AXZg8vwrqzL',
#   'ny4h6wmpKVbHZq7Q',
#   'NLMhDBTJw9zq8j2A',
#   'gjvwPqda6KpJ7z3k',
#   'mhbxMrLVFAyDt3Pz',
#   'V2Q4mHvJ8Pg1KTX6',
#   'qFfXM34xTdNaB87V',
#   'XDk2aVCLnyBFKHPr',
# ] )
