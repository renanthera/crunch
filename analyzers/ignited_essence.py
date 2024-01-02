import wcl
from .helper import *

def ignited_essence_debuff( event, event_data ):
  source_id = event.get( 'sourceID' )
  ignited_essence = event_data.get( 'ignited_essence' )
  params = event_data.get( 'params' )
  match event.get( 'type' ):
    case 'applydebuffstack':
      stack = event.get( 'stack' )
      ignited_essence.update( {
        source_id: stack
      } )
    case 'applydebuff':
      ignited_essence.update( {
        source_id: 1
      } )
    case 'removedebuff':
      if ignited_essence.get( source_id ) != 5:
        print( '   ', wcl.getPlayerFromID( source_id, params ), ignited_essence.get( source_id ) )
      ignited_essence.pop( event.get( 'sourceID' ) )

def emberscars_mark_debuff( event, event_data ):
  target_id = event.get( 'targetID' )
  emberscars_mark = event_data.get( 'emberscars_mark' )
  match event.get( 'type' ):
    case 'applydebuff':
      emberscars_mark.update( {
        target_id: 1
      } )
    case 'removedebuff':
      emberscars_mark.update( {
        target_id: 0
      } )

def devour_essence_cast( _, event_data ):
  print( '  Devour Essence', event_data.get( 'slam_count' ) )
  event_data[ 'slam_count' ] += 1
  for player, status in event_data[ 'emberscars_mark' ].items():
    if status:
      event_data[ 'ignited_essence' ].update( {
        player: 0
      } )

def ignited_essence( reportCodes ):
  callbacks = {
    421858: ignited_essence_debuff,
    421643: emberscars_mark_debuff,
    422277: devour_essence_cast
  }
  report_code_to_events(
    reportCodes,
    {
      'filterExpression':
      'ability.id in (421858, 421643) or (type = \'cast\' and ability.id = 422277)'
    },
    lambda fight: fight.get( 'name' ) == 'Smolderon',
    {
      'emberscars_mark': {},
      'ignited_essence': {},
      'slam_count': 1
    },
    callbacks,
    'abilityGameID'
  )
