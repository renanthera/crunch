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

# def tier_proc_analysis( info ):
#   reportCode = info.get( 'reportCode' )
#   startTime = info.get( 'startTime' )
#   endTime = info.get( 'endTime' )
#   id = info.get( 'id' )
#   name = info.get( 'name' )

#   filter_exprn = "\"source.name = '" + name + "' and ((type in ('applydebuff', 'removedebuff') and ability.id = 123725) or (type = 'damage'))\""
#   events = wcl.getEvents(
#     reportCode,
#     None,
#     {
#       'startTime': startTime,
#       'endTime': endTime,
#       'useAbilityIDs': 'true',
#       'filterExpression': filter_exprn,
#       'sourceID': id
#     }
#   )
#   data = list( chain.from_iterable( events.data ) )

#   debuff_active = defaultdict( int )
#   total = defaultdict( int )
#   active_targets = {}
#   for event in data:
#     ident = str( event.get( 'targetID', 0 ) ) + '-' + str( event.get( 'targetInstance', 0 ) )
#     spellid = event.get( 'abilityGameID', -1 )
#     match event.get( 'type' ):
#       case 'applydebuff':
#         if spellid == 123725:
#           active_targets.update( {
#             ident: True
#           } )
#       case 'removedebuff':
#         if spellid == 123725:
#           active_targets.update( {
#             ident: False
#           } )
#       case 'refreshdebuff':
#         continue
#       case 'damage':
#         # print(event)
#         total[ spellid ] += 1
#         if active_targets.get( ident ):
#           debuff_active[ spellid ] += 1
#         continue
#       case _:
#         # print('FELL THROUGH')
#         # print(event)
#         continue
#   # for k,v in active_targets.items():
#   #     print(k, v)
#   # for k,v in debuff_active.items():
#   #     print(k, v, total[k])
#   def sum_hits( whitelist, match_total ):
#     sum = 0
#     for spellid in total.keys():
#       if spellid in whitelist:
#         if match_total:
#           sum += total.get( spellid, 0 )
#         else:
#           sum += debuff_active.get( spellid, 0 )
#     return sum

#   whitelist_trigger_4p = [
#       1,      # melee hit
#       185099, # rising sun kick hit
#       115129, # expel harm hit
#       132467, # chi wave hit
#       # chi burst hit
#       # 196608, # eye of the tiger dot
#       391400, # resonant fists hit
#       121253, # keg smash hit
#       148187, # rushing jade wind hit
#               # special delivery hit
#       115181, # breath of fire hit
#       # 123725, # breath of fire dot
#       386959, # charred passions hit
#       387621, # dragonfire brew hit
#       # 325217, # bonedust brew hit
#       325153, # exploding keg hit
#       388867, # exploding keg proc
#       # press the advantage
#       # 393786, # chi surge dot
#       205523, # blackout kick hit
#       # 117952, # crackling jade lightning dot
#       107270, # spinning crane kick hit
#       100780, # tiger palm hit
#       322109, # touch of death hit
#       389541, # claw of the white tiger hit
#       1,      # niuzao melee hit
#       227291, # niuzao stomp hit
#   ]
#   whitelist_trigger_2p = [
#       115181, # breath of fire hit
#       123725, # breath of fire dot
#   ]
#   triggers_total = sum_hits( [ 425299 ], True )
#   triggers_2p = sum_hits( whitelist_trigger_2p, True )
#   triggers_4p = triggers_total - triggers_2p
#   candidates_4p = sum_hits( whitelist_trigger_4p, False )
#   if candidates_4p == 0:
#     print( 'NO 4p TRIGGER CANDIDATES' )
#     return
#   ratio = triggers_4p / candidates_4p
#   # print(triggers_total, triggers_2p, triggers_4p, candidates_4p)
#   print( ratio )

# # runReports(tier_proc_analysis)
# # runReports(tier_guard_analysis)

# # wcl.Request(wcl.PointsSpent())
# # wcl.getPointsSpent()

# import json

import analyzers

analyzers.ignited_essence( [ 'YftHvBKJzh8nxa9A', 'xrfcz1d34vjJ2LqM' ] )
wcl.getPointsSpent()
