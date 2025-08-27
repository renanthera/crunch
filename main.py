import analyzers
import wcl
import cProfile

# analyzers.overwhelming_force.coefficient( [
#   # strongboi
#   'CvKQW1AdD42wmMz3',
#   'gWMFdXk2pnL4fcx6',
#   'hGd96NyZ8v7Hpw34',
#   'HG2xLYBJVyvDPK6t',
#   'F1mZrfCP4MqK7dHg',
#   'v7KBtzr4jhN3TgGk',
#   'WtgAvP9N2aTFQJmr',
#   # malmie
#   'DXfYn9xA3jCPdVwp',
#   '9v1FZtJQGMC7qx8m',
#   '7JxTBf2DPKYht9vj',
#   '83bjtyX7ZzdWJ9HQ',
#   'CjTMhxdKwFgR7Pqc',
#   'X1WYaDcBvMrQmRpV',
#   'X7GzLdh8VB3q2MAb',
#   'ThpGywvM4BFcPx2b',
#   # dwarf
#   # 'QCyrLh7tG91B3TMP',
#   # 'PkrFRp28mXMwNTjJ',
#   # 'WT3VJ8dMknhAL7XB',
#   # 'NvPQc2YA1VnqkRMg'
# ] )

# analyzers.dual_threat.probability_at_count( [ 'gqyW1GPaYfX3mzKn' ] )

# analyzers.dual_threat.probability_at_count( [ 'BgRnxTbyjAp3aDrF' ] )
# analyzers.dual_threat.probability_at_count( [ '6KT2BAqVgFrywmGx' ] )
# analyzers.dual_threat.probability_aggregate('BgRnxTbyjAp3aDrF','6KT2BAqVgFrywmGx')

# analyzers.tww3_moh_2p.probability_at_count(['JymjCVKqcTGr1nL8'])

# analyzers.tww3_moh_2p.probability_at_count(['xHz4a8mnB2pLcAfP'])
# analyzers.tww3_moh_2p.probability_at_count(['dGchmDzq6xQ4Zwkb'])
# analyzers.tww3_moh_2p.probability_at_count(['2wRmB64JybnXzp7K'])
# analyzers.tww3_moh_2p.probability_at_count(['xHz4a8mnB2pLcAfP','dGchmDzq6xQ4Zwkb','2wRmB64JybnXzp7K'])

# analyzers.tww3_moh_2p.probability_at_count([# 'JymjCVKqcTGr1nL8',
#                                             'dGchmDzq6xQ4Zwkb','xHz4a8mnB2pLcAfP','prRJahHm7kFCWTVD'])

# talent = [ 125039, 124865, 125008 ]
# items = [ 237673, 237671, 237676, 237672, 237674 ]
# def entry_match_fn( id, items ):
#   return lambda combatant_info: [
#     talent.get( 'id' ) in id
#     for talent in [
#         entry
#         for tree in [ 'talentTree', 'talent_tree' ]
#         for entry in combatant_info.get( tree, [] )
#     ]
#   ].count(True) == len(talent) and [
#     item.get('id') in items
#     for item in combatant_info.get( 'gear', [] )
#     ].count(True) >= 4
# codes = [
#   report
#   for report in wcl.getReportCodes( {
#       'zoneID': 45,
#       'pagination_limit': 10,
#   } )
#   if report.get('startTime') > 1753747200000
# ]
# dedupe = []
# filtered_codes = [
#   report.get('code')
#   for report in codes
#   # if report.get('code') == 'JymjCVKqcTGr1nL8'
#   if ( fights := wcl.getFights(report) )
#   if ( report.update( { 'startTime': min([f.get('startTime') for f in fights]),
#                         'endTime': max([f.get('endTime') for f in fights])}) ) or True
#   # if ( p := print(wcl.getPlayerWith(report, entry_match_fn(talent, items)))) or True
#   if ( sources := wcl.getPlayerWith( report, entry_match_fn( talent, items ) ) )
#   # if ( event_fingerprint := wcl.getEvents( report + { 'limit': 10 } ) ) or True
#   # if event_fingerprint not in dedupe
#   # if ( _ := dedupe.append(event_fingerprint) ) or True
# ]
# print(filtered_codes)
# print(len(filtered_codes))

# wcl.getPointsSpent()
# analyzers.tww3_moh_2p.probability_at_count( filtered_codes )

# analyzers.manaforge_omega.plexus_sentinel()

# analyzers.tww3_moh_2p_v2.trailing_window_size()
analyzers.tww3_moh_2p_v2.match_trigger_windows()
# cProfile.run('analyzers.tww3_moh_2p_v2.windows()')
