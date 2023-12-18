import json

from . import query
from .requests import Request

def getFights( params ):
  return Request( query.Fights( params ) ).data

def getPlayerDetails( params ):
  return Request( query.PlayerDetails( params )
                 ).data.get( 'data' ).get( 'playerDetails' ) # pyright: ignore

def getMasterData( params ):
  return Request( query.MasterData( params ) ).data

def getEvents( params ):
  return Request( query.Events( params ) ).data.get( 'data' ) # pyright: ignore

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
  return print(
    req,
    'point'  if req == 1 else 'points',
    'spent this hour'
  ) # pyright: ignore
