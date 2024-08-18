from .helper import *
from copy import deepcopy

bok = 205523
fob = 457271

def fmt_timestamp( timestamp ):
  timestamp_s = timestamp // 1000
  timestamp_m = timestamp_s // 60
  timestamp_h = timestamp_m // 60
  return f'{timestamp_h%60:02}:{timestamp_m%60:02}:{timestamp_s%60:02}.{timestamp%1000:03}'

def cb( self, event ):
  if event.get( 'sourceID' ) not in self.event_data[ 'info' ].keys():
    self.event_data[ 'info' ][ event.get( 'sourceID' ) ] = deepcopy( self.event_data[ 'info_base' ] )

  info = self.event_data[ 'info' ][ event.get( 'sourceID' ) ]

  if event.get( 'abilityGameID' ) == fob:
    info[ 'has_applied' ] = True

  if event.get( 'abilityGameID' ) == bok:
    if info[ 'previous' ] is not None and info.get( 'previous', {} ).get( 'abilityGameID' ) == fob:
      info[ 'data' ][ info[ 'count_since_last' ] ][ 'successful' ] += 1
      info[ 'count_since_last' ] = 0
    else:
      info[ 'data' ][ info[ 'count_since_last' ] ][ 'failed' ] += 1
      info[ 'count_since_last' ] += 1

  if False:
    print( fmt_timestamp( event.get('timestamp') - self.params['startTime'] ), end=' ' )
    print( event.get( 'sourceID' ), end='\t')
    if event.get( 'abilityGameID' ) == bok:
      print( "BOK", info[ 'count_since_last' ] )
    if event.get( 'abilityGameID' ) == fob:
      print( "FOB" )

  info[ 'previous' ] = event

def counts( report_codes ):
  clause_1 = f"type = 'applybuff' and ability.id = {fob}"
  clause_2 = f"type = 'cast' and ability.id = {bok}"
  t = Analyzer(
    report_codes,
    params={
      'limit': 25000,
      'filterExpression': f"({clause_1}) or ({clause_2})"
    },
    callbacks=[
      {
        'any': True,
        'callback': cb
      }
    ],
    event_data={
      'info_base': {
        'data': [
          { 'index': k, 'failed': 0, 'successful': 0 }
          for k in range(0, 30)
        ],
        'count_since_last': 0,
        'has_applied': False,
        'previous': None
      },
      'info': {}
    },
  )

  import json
  # print(json.dumps(t.data, indent=2))
  o = {}
  for fight in t.data:
    for player, data in fight[ 'event_data' ][ 'info' ].items():
      for index in data[ 'data' ]:
        o.setdefault(index['index'], {'SUCCESS': 0, 'FAIL': 0})
        o[index['index']]['SUCCESS'] += index['successful']
        o[index['index']]['FAIL'] += index['failed']

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
