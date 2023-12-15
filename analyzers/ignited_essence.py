import wcl

params = {
  'reportCode': 'YftHvBKJzh8nxa9A'
}

def ignited_essence( reportCodes ):
  for reportCode in reportCodes:
    print( '===================================' )
    print( 'report code:', reportCode )
    print( '===================================' )
    params = {
      'reportCode': reportCode,
      'startTime': 0,
      'endTime': 1e30,
      'args': {
        'dataType': 'Debuffs',
        'abilityID': 421858
      }
    }

    fights = wcl.getFights( params )
    fights = [
      fight for fight in fights.data if fight.get( 'name' ) == 'Smolderon'
    ] # pyright: ignore

    fight_offset = fights[ 0 ].get( 'id' )

    for fight in fights:
      print( fight.get( 'id' ) - fight_offset + 1 )
      params.update( {
        'startTime': fight.get( 'startTime' ),
        'endTime': fight.get( 'endTime' )
      } )

      players = wcl.getPlayerDetails( params ).data.get( 'data' ).get(
        'playerDetails'
      ) # pyright: ignore
      players = [ char for role in players.values() for char in role ]

      def get_player_name( id ):
        for player in players: # pyright: ignore
          if player.get( 'id' ) == id:
            return player.get( 'name' )

      debuff_tracker = {}
      events = wcl.getEvents( params )
      for event in events:
        sourceID = event.get( 'sourceID' )
        match event.get( 'type' ):
          case 'applydebuffstack':
            stack = event.get( 'stack' )
            debuff_tracker.update( {
              sourceID: stack
            } )
          case 'applydebuff':
            debuff_tracker.update( {
              sourceID: 1
            } )
          case 'removedebuff':
            if debuff_tracker.get( sourceID ) != 5:
              print( '-', get_player_name( sourceID ), debuff_tracker.get( sourceID ) )
            debuff_tracker.pop( event.get( 'sourceID' ) )
