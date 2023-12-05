from .requests import *
from .query import *

def getSegments( reportCode ):
  return Request( ReportInfo( reportCode ) )

def getPlayerInfo( reportCode, startTime, endTime ):
  return Request( PlayerInfo( reportCode, startTime, endTime ) )

def getMasterData( reportCode ):
  return Request( MasterData( reportCode ) )

def getEvents( reportCode, fields, args ):
  return Request( Events( reportCode, args, fields ) )

def printPlayerInfo( reportCode, startTime, endTime ):
  req = getPlayerInfo( reportCode, startTime, endTime )
  assert(req.data is not None)
  for entry in req.data:
    players = entry.get( 'playerDetails' )
    for role, player_list in players.items():
      print( '  ', role )
      for player in player_list:
        print(
          '    ',
          player.get( 'id' ),
          player.get( 'name' ),
          player.get( 'type' ),
          player.get( 'specs' ),
        )

def getPointsSpent():
  return Request( PointsSpent() )
