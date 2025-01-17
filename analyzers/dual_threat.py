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

  players = [
    f"'{player}'"
    for player in wcl.getPlayerNameWith( self.params, entry_match_fn( 125020 ) )
  ]
  player_names = ', '.join( players )
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
      # 'filterExpression': "ability.id in (1, 451839) and source.name = 'Pepeg'"
      'filterExpression': "type='combatantinfo'"
    },
    callbacks=[
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
    fight_params_update=fight_params_update
  )

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

  l = [
    ( key, value['SUCCESS'], value['FAIL'] )
    for key, value in o.items()
  ]

  x = [
    v[0]
    for v in l
    if ( v[1] or v[2] )
  ]

  y = [
    v[1]
    for v in l
    if ( v[1] or v[2] )
  ]

  z = [
    v[2]
    for v in l
    if ( v[1] or v[2] )
  ]

  p = [
    y[i] / ( y[i] + z[i] )
    for i in range(len(z))
  ]

  print('successes', sum(y))
  print('fails', sum(z))
  print('attempts', sum(y) + sum(z))

  import matplotlib.pyplot as plt
  plt.style.use('dark_background')
  _, ax = plt.subplots(2,3)
  ax[0, 0].set_xlabel('number of consecutive failures')
  ax[0, 0].set_ylabel('success')
  ax[0, 0].scatter(x, y)
  ax[0, 1].set_xlabel('number of consecutive failures')
  ax[0, 1].set_ylabel('fail')
  ax[0, 1].scatter(x, z)
  ax[0, 2].set_xlabel('number of consecutive failures')
  ax[0, 2].set_ylabel('P(X=x)')
  ax[0, 2].scatter(x, p)
  ax[1, 0].set_xlabel('number of consecutive failures')
  ax[1, 0].set_ylabel('P(X>=x)')
  ax[1, 0].scatter(x, [sum(p[index:]) for index in range(len(x))])
  ax[1, 1].set_xlabel('number of consecutive failures')
  ax[1, 1].set_ylabel('P(X<=x)')
  ax[1, 1].scatter(x, [sum(p[:index+1]) for index in range(len(x))])
  ax[1, 2].set_xlabel('number of consecutive failures')
  ax[1, 2].set_ylabel('accumulated successes / accumulated failures')
  ax[1, 2].scatter(x, [sum(y[:index+1]) / ( sum(y[:index+1]) + sum(z[:index+1])) for index in range(len(x))])

  plt.show()
