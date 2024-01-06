from .helper import *
from wcl import getPlayerFromID, getPlayers

import matplotlib.pyplot as plot
import json

# NOTES:
# Not all seeds spawned from Flaming Germination spawn at the same time.

TEXT_REPORT = False
GRAPHICAL_REPORT = False

def capture_types( event, event_data ):
  t = event.get( 'type' )
  event_keys = { key
                 for key in event.keys() }
  if t in event_data[ 'types' ].keys():
    event_data[ 'types' ][ t ].update( event_keys )
  else:
    event_data[ 'types' ].update( {
      t: event_keys
    } )

def update_pos( event, event_data ):
  if event.get( 'targetID' ) and event.get( 'x' ) and event.get( 'y' ):
    event_data[ 'positions' ].update( {
      event.get( 'targetID' ): {
        'x': event.get( 'x' ),
        'y': event.get( 'y' )
      }
    } )

def relative_pos( pos1, pos2 ):
  return {
    'x': pos1.get( 'x' ) - pos2.get( 'x' ),
    'y': pos1.get( 'y' ) - pos2.get( 'y' )
  }

def soak_seed( event, event_data ):
  target_id = event.get( 'targetID' )
  target_name = getPlayerFromID( target_id, event_data[ 'params' ] )
  player_pos = event_data[ 'positions' ].get( target_id )
  boss_pos = event_data[ 'positions' ].get( 2 )
  relative = relative_pos( player_pos, boss_pos )
  timestamp = event.get( 'timestamp' )
  delta = timestamp - event_data[ 'last_cast' ]
  last_soak = event_data[ 'last_soak' ].get( target_id, 0 )
  if last_soak >= event_data[ 'last_cast' ]:
    event_data[ 'double_soakers' ][ target_id ] += 1
  else:
    event_data[ 'soak_locations' ].append( {
      'x': relative['x'],
      'y': relative['y'],
      'latency': delta
    } )
    event_data[ 'soak_latency' ][ target_id ].append( delta )
  event_data[ 'last_soak' ].update( {
    target_id: timestamp
  } )
  if TEXT_REPORT:
    print( f'\t{target_name} soaked at {relative} after {delta} milliseconds' )
    if last_soak >= event_data[ 'last_cast' ]:
      print( f'\t!!!!{target_name} double soaked!!!!' )

def boss_cast( event, event_data ):
  target_id = event.get( 'targetID' )
  target_name = 'Tindral Sageswift'
  position = event_data[ 'positions' ].get( target_id )
  event_data[ 'last_cast' ] = event.get( 'timestamp' )
  event_data[ 'candidate_to_soak' ].update( {
    player: count + 1
    for player,
    count in event_data[ 'candidate_to_soak' ].items()
    if event_data[ 'alive_players' ].get( player )
  } )
  if TEXT_REPORT:
    print( f'{target_name} casts at {position}' )

def death( event, event_data ):
  event_data[ 'alive_players' ].update( {
    event.get( 'targetID' ): False
  } )

def initialize_objects( _, event_data ):
  players = getPlayers( event_data[ 'params' ] )
  event_data[ 'alive_players' ] = {
    player.get( 'id' ): True
    for player in players
  }
  event_data[ 'candidate_to_soak' ] = {
    player.get( 'id' ): 0
    for player in players
  }
  event_data[ 'double_soakers' ] = {
    player.get( 'id' ): 0
    for player in players
  }
  event_data[ 'soak_latency' ] = {
    player.get( 'id' ): []
    for player in players
  }

def flaming_germination( reportCodes ):
  event_data_base = {
    'types': {},
    'positions': {},
    'last_soak': {},
    'soak_latency': {},
    'alive_players': {},
    'candidate_to_soak': {},
    'double_soakers': {},
    'soak_locations': [],
    'last_cast': 0
  }
  data = report_code_to_events(
    reportCodes,
    {
      'limit':
      25000,
      'includeResources':
      True,
      'filterExpression':
      "type in ('damage', 'resourcechange', 'cast', 'heal', 'drain', 'encounterstart', 'death')"
    },
    lambda fight: fight.get( 'name' ) == 'Tindral Sageswift, Seer of the Flame',
    event_data_base,
    [
      {
        'type': 'damage',
        'abilityGameID': 430584,
        'callback': soak_seed
      },
      {
        'type': 'cast',
        'abilityGameID': 423265,
        'callback': boss_cast
      },
      {
        'any': True,
        'callback': update_pos
        # 'callback': lambda e, e_d: ( capture_types( e, e_d ), update_pos( e, e_d ) ) # yapf: disable
      },
      {
        'type': 'encounterstart',
        'callback': initialize_objects
      },
      {
        'type': 'death',
        'callback': death
      }
    ]
  )

  position_data = flatten_event_data( data, event_data_base )[ 'soak_locations' ]
  if TEXT_REPORT:
    latency_data = {
      player: {
        'latencies':
        [
          latency
          for report_data in data.values()
          for fight_data in report_data.values()
          for p, latencies in fight_data['soak_latency'].items()
          if p == player
          for latency in latencies
        ],
        'candidate_to_soak': sum( [
          count
          for report_data in data.values()
          for fight_data in report_data.values()
          for p, count in fight_data['candidate_to_soak'].items()
          if p == player
        ] ),
        'double_soaks': sum( [
          count
          for report_data in data.values()
          for fight_data in report_data.values()
          for p, count in fight_data['candidate_to_soak'].items()
          if p == player
        ] )
      }
      for report_data in data.values()
      for fight_data in report_data.values()
      for player in fight_data['soak_latency'].keys()
    } # yapf: disable


    params = data[ reportCodes[ 0 ] ][ 0 ][ 'params' ]
    output = []
    for player_id, vals in latency_data.items():
      player_name = getPlayerFromID( player_id, params )
      latencies = vals.get( 'latencies', [] )
      soak_count = len( latencies )
      mean_latency = sum( latencies ) / soak_count
      candidate_to_soak = vals.get( 'candidate_to_soak' )
      output.append( {
        'name': player_name,
        'latencies': latencies,
        'mean_latency': mean_latency,
        'soak_count': soak_count,
        'candidate_to_soak': candidate_to_soak,
        'double_soaks': vals.get( 'double_soaks' )
      } )

    output = sorted( output, key=lambda e: e.get( 'mean_latency' ) )
    print(json.dumps(output, indent=2))
    print(json.dumps(position_data, indent=2))

  if GRAPHICAL_REPORT:
    plot.style.use( 'dark_background' )
    colors = [ l.get('latency') for l in position_data ]
    shortest_soak = min(colors)
    longest_soak = max(colors)
    colors = [
      (color - shortest_soak) / (longest_soak - shortest_soak)
      for color in colors
    ] + [ 0 ]
    points = [ [ l.get( t ) for l in position_data ] + [0] for t in [ 'x', 'y' ] ]
    plot.scatter(
      *points,
      c=colors,
      cmap="jet"
    )
    plot.colorbar()
    plot.show()


  # def set_default( obj ):
  #   if isinstance( obj, set ):
  #     return list( obj )
  #   raise TypeError

  # import json
  # for report_code, report_data in data.items():
  #   for fight_id, fight_data in report_data.items():
  #     print(json.dumps(fight_data['types'], indent=2, default=set_default))
