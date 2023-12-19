import wcl
# import math

# from analyzers import Stagger

# from itertools import chain
# from collections import defaultdict

# def fmt( v ):
#   vals = 'kmbt'
#   digits = math.floor( math.log10( v ) )
#   index = math.floor( digits / 3 )
#   if ( index > 0 ):
#     return f'{round(v / 10 ** ( index * 3), 1)}{vals[index - 1]}'
#   return f'{round(v, 1)}'

# def t( ms ):
#   seconds = ms / 1000
#   minutes = math.floor( seconds / 60 )
#   hours = math.floor( minutes / 60 )
#   remainder = seconds - 60 * ( minutes + 60 * hours )
#   sec = math.floor( remainder )
#   dec = str( round( remainder - sec, 3 ) )[ 2: ]
#   return '{hours:0=2}:{minutes:0=2}:{sec:0=2}.{dec:0<3}'.format(
#     hours=hours,
#     minutes=minutes,
#     dec=dec,
#     sec=sec
#   )

# def p( d ):
#   for e in d.data:
#     print( e )

# def reports():
#   return {
#     'affinitym-11/25-a': {
#       'reportCode': '48WF9r1QMZLaCdxm',
#       'name': 'AffinityM',
#       'startTime': 4028035,
#       'endTime': 5649260,
#       'id': '6',
#       'added': '11/25',
#       'reason': 't31 4p proc analysis',
#       'complete': True
#     },
#     'affinitym-11/25-b': {
#       'reportCode': '48WF9r1QMZLaCdxm',
#       'name': 'AffinityM',
#       'startTime': 1585659,
#       'endTime': 3304850,
#       'id': '6',
#       'added': '11/25',
#       'reason': 't31 4p proc analysis'
#     },
#     'relowindi-11/23-a': {
#       'reportCode': '1kZbDcdynvL9YQqm',
#       'name': 'Relowindi',
#       'startTime': 6885007,
#       'endTime': 7928641,
#       'id': '366',
#       'added': '11/25',
#       'reason': 't31 4p proc analysis',
#       'complete': True
#     },
#     'relowindi-11/23-b': {
#       'reportCode': '1kZbDcdynvL9YQqm',
#       'name': 'Relowindi',
#       'startTime': 8100157,
#       'endTime': 9162810,
#       'id': '366',
#       'added': '11/25',
#       'reason': 't31 4p proc analysis'
#     },
#     'relowindi-11/23-b': {
#       'reportCode': '1kZbDcdynvL9YQqm',
#       'name': 'Relowindi',
#       'startTime': 8100157,
#       'endTime': 9162810,
#       'id': '366',
#       'added': '11/25',
#       'reason': 't31 4p proc analysis'
#     },
#     'captclit-11/21-a': {
#       'reportCode': 'zNGTmYPXwDtVKAkd',
#       'name': 'Captclit',
#       'startTime': 53519791,
#       'endTime': 55220108,
#       'id': '216',
#       'added': '11/25',
#       'reason': 't31 4p proc analysis',
#       'complete': True
#     },
#     'captclit-11/21-b': {
#       'reportCode': 'zNGTmYPXwDtVKAkd',
#       'name': 'Captclit',
#       'startTime': 55470186,
#       'endTime': 56863302,
#       'id': '216',
#       'added': '11/25',
#       'reason': 't31 4p proc analysis'
#     },
#     'captclit-11/21-c': {
#       'reportCode': 'zNGTmYPXwDtVKAkd',
#       'name': 'Captclit',
#       'startTime': 57233811,
#       'endTime': 58774201,
#       'id': '216',
#       'added': '11/25',
#       'reason': 't31 4p proc analysis'
#     },
#     'captclit-11/21-d': {
#       'reportCode': 'zNGTmYPXwDtVKAkd',
#       'name': 'Captclit',
#       'startTime': 59366032,
#       'endTime': 60930109,
#       'id': '216',
#       'added': '11/25',
#       'reason': 't31 4p proc analysis'
#     },
#     'captclit-11/21-e': {
#       'reportCode': 'zNGTmYPXwDtVKAkd',
#       'name': 'Captclit',
#       'startTime': 63021215,
#       'endTime': 64401331,
#       'id': '216',
#       'added': '11/25',
#       'reason': 't31 4p proc analysis'
#     },
#     'captclit-11/21-f': {
#       'reportCode': 'zNGTmYPXwDtVKAkd',
#       'name': 'Captclit',
#       'startTime': 65919901,
#       'endTime': 67625510,
#       'id': '216',
#       'added': '11/25',
#       'reason': 't31 4p proc analysis'
#     },
#   }

# def isComplete():
#   complete = {}
#   for v in reports().values():
#     reportCode = v.get( 'reportCode' )
#     if not complete.get( reportCode ):
#       complete.update( {
#         reportCode: v.get( 'complete',
#                            False )
#       } )
#     else:
#       if complete.get( reportCode ) and v.get( 'complete', False ):
#         complete.update( {
#           reportCode: True
#         } )
#   return complete

# def getSegments():
#   complete = isComplete()
#   for k, v in complete.items():
#     if not v:
#       p( wcl.getSegments( k ) )

# def getPlayerInfo():
#   complete = isComplete()
#   for u, w in reports().items():
#     reportCode = w.get( 'reportCode', False )
#     startTime = w.get( 'startTime', False )
#     endTime = w.get( 'endTime', False )
#     if not ( reportCode and startTime and endTime ):
#       continue
#     if not complete.get( reportCode ):
#       print( u )
#       wcl.printPlayerInfo( reportCode, startTime, endTime )

# def runReports( fn ):
#   for name, info in reports().items():
#     print( name )
#     fn( info )

# getSegments()
# getPlayerInfo()

# # p(wcl.getMasterData(reportCode))

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

# analyzers.ignited_essence( [ 'YftHvBKJzh8nxa9A', 'xrfcz1d34vjJ2LqM' ] )
# analyzers.ignited_essence( [ 'qWJXamNtPbTfZ41y' ] )

# analyzers.t31_brew.proc( [ 'qWJXamNtPbTfZ41y', '7Qct4AXZg8vwrqzL' ] )

# analyzers.t31_brew.proc( [ '48WF9r1QMZLaCdxm', '1kZbDcdynvL9YQqm', 'zNGTmYPXwDtVKAkd' ] )

analyzers.t31_brew.proc( [
  'bkrPDQ1ZtTGRphWn',
  'YftHvBKJzh8nxa9A',
  'qWJXamNtPbTfZ41y',
  '7Qct4AXZg8vwrqzL',
  'ny4h6wmpKVbHZq7Q',
  'NLMhDBTJw9zq8j2A',
  'gjvwPqda6KpJ7z3k',
  'mhbxMrLVFAyDt3Pz',
  'V2Q4mHvJ8Pg1KTX6',
  'qFfXM34xTdNaB87V',
  'XDk2aVCLnyBFKHPr',
] )
wcl.getPointsSpent()
