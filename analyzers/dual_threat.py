from .helper import *
from copy import deepcopy
import wcl

def fight_params_update( self ):
  def entry_match_fn( id ):
    return lambda combatant_info: any( [
      talent.get( 'id' ) == id
      for talent in [
          entry
          for tree in [ 'talentTree', 'talent_tree' ]
          for entry in combatant_info.get( tree, [] )
      ]
    ] )

  # players = [
  #   f"'{player}'"
  #   for player in wcl.getPlayerNameWith( self.params, entry_match_fn( 125020 ) )
  # ]
  # player_names = ', '.join( players )
  player_names = 'Pepeg'
  clause_0 = f"(source.name in ({player_names}))"

  clause_2_ids = [ 1, 451839 ]
  clause_2 = f"(ability.id in ({', '.join((str(x) for x in clause_2_ids))}))"

  clauses = ' or '.join( [
    clause_2
  ] )
  return {
    'filterExpression': f"{clause_0} and ({clauses})"
  }

def fmt_timestamp( timestamp ):
  timestamp_s = timestamp // 1000
  timestamp_m = timestamp_s // 60
  timestamp_h = timestamp_m // 60
  return f'{timestamp_h%60:02}:{timestamp_m%60:02}:{timestamp_s%60:02}.{timestamp%1000:03}'

def cb( self, event ):
  if event.get( 'sourceID' ) not in self.event_data[ 'info' ].keys():
    self.event_data[ 'info' ][ event.get( 'sourceID' ) ] = deepcopy( self.event_data[ 'info_base' ] )

  if ( event.get( 'hitType') == 0 ):
    return

  info = self.event_data[ 'info' ][ event.get( 'sourceID' ) ]
  if event.get( 'abilityGameID' ) == 1:
    info[ 'count_since_last' ] += 1
  if event.get( 'abilityGameID' ) == 1:
    info[ 'data' ][ info[ 'count_since_last' ] ][ 'failed' ] += 1
  if event.get( 'abilityGameID' ) == 451839:
    info[ 'data' ][ info[ 'count_since_last' ] ][ 'successful' ] += 1
    info[ 'count_since_last' ] = 0

  if False:
    print( fmt_timestamp( event.get('timestamp') - self.params['startTime'] ), end=' ' )
    print( event.get( 'sourceID' ), end='\t')
    if event.get( 'abilityGameID' ) == 1:
      print( "MELEE", info[ 'count_since_last' ], event.get( 'hitType' ) )
    if event.get( 'abilityGameID' ) == 451839:
      print( "DUAL THREAT" )

def probability_at_count( report_codes ):
  t = Analyzer(
    report_codes,
    params={
      'limit': 25000,
      'filterExpression': "ability.id in (1, 451839) and source.name = 'Pepeg'"
      # 'filterExpression': "type='combatantinfo'"
    },
    callbacks=[
      {
        'any': True,
        'callback': lambda _, e: print(e)
      },
      {
        'type': 'damage',
        'abilityGameID': [ 1, 451839 ],
        'callback': cb
      }
    ],
    event_data={
      'info_base': {
        'data': [
          { 'index': k, 'failed': 0, 'successful': 0 }
          for k in range(0, 30)
        ],
        'count_since_last': 0
      },
      'info': {}
    },
    # fight_params_update=fight_params_update
  )

  import json
  # print(json.dumps( t.data, indent=2))

  o = {}
  for fight in t.data:
    for player, data in fight[ 'event_data' ][ 'info' ].items():
      for index in data[ 'data' ]:
        o.setdefault(index['index'], {'SUCCESS': 0, 'FAIL': 0})
        o[index['index']]['SUCCESS'] += index['successful']
        o[index['index']]['FAIL'] += index['failed']
        # if index[ 'index' ] > 14 and ( index[ 'failed' ] + index[ 'successful' ] > 0 ):
        #   print( fight[ 'report_code' ], fight[ 'fight_id' ] )
        #   print( player )
        #   print( index )

  print(json.dumps(o, indent=2))
  l = [
    ( index, success, fail )
    for key, value in o.items()
    if ( index := key )
    if ( success := value['SUCCESS'] )
    if ( fail := value['FAIL'] )
  ]
  print(l)

  import matplotlib.pyplot as plt
  import numpy as np

  x = [
    u
    for v in l
    if ( u := v[0] )
  ]

  y = [
    u
    for v in l
    if ( u := v[1] / ( v[1] + v[2] ) )
  ]

  plt.style.use('dark_background')
  plt.scatter(x, y)
  plt.show()
  # m = max( max( [
  #   [
  #     index[ 'index' ] if index[ 'failed' ] > 0 or index[ 'successful' ] > 0 else 0
  #     for _, value in fight[ 'event_data' ][ 'info' ].items()
  #     for index in value[ 'data' ]
  #   ]
  #   for fight in t.data
  # ] ) )
  # print('\n\n')
  # print(m)
