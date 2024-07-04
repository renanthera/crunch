import json
from copy import deepcopy

from numpy import char

from . import query
from .requests import Request

def getFights( params ):
  return Request( query.Fights( params ) ).data

def getPlayerDetails( params ):
  return Request( query.PlayerDetails( params ) ).data.get( 'data', {} ).get( 'playerDetails', {} ) or {} # pyright: ignore

def getMasterData( params ):
  return Request( query.Actors( params ) ).data

def getEvents( params ):
  return Request( query.Events( params ) ).data.get( 'data', {} )

def getCombatantInfo( params ):
  params_copy = deepcopy( params )
  params_copy.update( {
    'filterExpression': "type in ('combatantinfo')"
  } )
  return Request( query.Events( params_copy ) ).data.get( 'data', [] )

def printFights( params ):
  req = getFights( params )
  assert req is not None, 'No fights data returned'

  fights = [ {
    'id': fight.get( 'id' ),
    'name': fight.get( 'name' ),
    'difficulty': fight.get( 'difficulty' ),
    'kill': fight.get( 'kill' ),
    'startTime': fight.get( 'startTime' ),
    'endTime': fight.get( 'endTime' )
  } for fight in req ]

  for fight in fights:
    print( json.dumps( fight, indent=2 ) )

def printPlayerDetails( params ):
  req = getPlayerDetails( params )
  assert req.data is not None

  for role, player_list in req.items():
    players = [ {
      'id': player.get( 'id' ),
      'name': player.get( 'name' ),
      'type': player.get( 'type' ),
      'specs': player.get( 'specs' )
    } for player in player_list ]
    print( role )
    for player in players:
      print( json.dumps( player, indent=2 ) )

def getPointsSpent():
  params = {}
  req = Request( query.PointsSpentThisHour( params ) ).data.get( 'pointsSpentThisHour' )
  return print( req, 'point' if req == 1 else 'points', 'spent this hour' ) # pyright: ignore

def getPlayerFromID( id, params ):
  for player in getPlayers( params ):
    if player.get( 'id' ) == id:
      return player.get( 'name' )

def getPlayers( params ):
  return [
    char
    for role in getPlayerDetails( params ).values()
    for char in role
  ]

def getPlayersBySpec( params, spec_filter ):
  return [
    player
    for player in getPlayers( params )
    if any( [ spec.get( 'spec' ) == spec_filter for spec in player[ 'specs' ] ] )
  ]

def getPlayerWith( params, match_fn ):
  return [
    combatant_info.get( 'sourceID' )
    for combatant_info in getCombatantInfo( params )
    if match_fn( combatant_info )
  ]

def getPlayerNameWith( params, match_fn ):
  return [
    getPlayerFromID(  combatant_info.get( 'sourceID' ), params )
    for combatant_info in getCombatantInfo( params )
    if match_fn( combatant_info )
  ]

def getPlayerNameWithTalent( params, talent_id ):
  def talent_match_fn( combatant_info ):
    talent_tree_names = [
      'talentTree', 'talent_tree'
    ]
    return any( [
      talent.get( 'spellID' ) == talent_id
      for talent in [
          entry
          for option in talent_tree_names
          for entry in combatant_info.get( option, [] )
      ]
    ] )
  return [
    getPlayerFromID( player_id, params )
    for player_id in getPlayerWith( params, talent_match_fn )
  ]
