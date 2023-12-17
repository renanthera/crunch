import wcl

def ignited_essence( reportCodes ):
  for reportCode in reportCodes:
    print( '===================================' )
    print( 'report code:', reportCode )
    print( '===================================' )
    params = {
      'code': reportCode,
      'startTime': 0,
      'endTime': 1e30,
      'filterExpression': 'ability.id in (421858, 421643) or (type = \'cast\' and ability.id = 422277)'
    } # yapf: disable

    fights = wcl.getFights( params )

    # TODO: better method for detecting if a fight is a reset
    fights = [
      fight for fight in wcl.getFights( params )
      if fight.get( 'name' ) == 'Smolderon' and fight.get( 'endTime' ) -
      fight.get( 'startTime' ) > 1000
    ]

    for fight in range( len( fights ) ):
      print( fight + 1 )

      params.update( {
        'startTime': fights[ fight ].get( 'startTime' ),
        'endTime': fights[ fight ].get( 'endTime' )
      } )

      players = wcl.getPlayerDetails( params )
      players = [ char for role in players.values() for char in role ]

      def get_player_name( id ):
        for player in players:
          if player.get( 'id' ) == id:
            return player.get( 'name' )

      events = wcl.getEvents( params )

      emberscar_mark = {}
      ignited_essence = {}
      slam_count = 1

      for event in events: # pyright: ignore
        sourceID = event.get( 'sourceID' )
        targetID = event.get( 'targetID' )
        match event.get( 'abilityGameID' ):
          case 421858:
            match event.get( 'type' ):
              case 'applydebuffstack':
                stack = event.get( 'stack' )
                ignited_essence.update( {
                  sourceID: stack
                } )
              case 'applydebuff':
                ignited_essence.update( {
                  sourceID: 1
                } )
              case 'removedebuff':
                if ignited_essence.get( sourceID ) != 5:
                  print( '   ', get_player_name( sourceID ), ignited_essence.get( sourceID ) )
                ignited_essence.pop( event.get( 'sourceID' ) )
          case 421643:
            match event.get( 'type' ):
              case 'applydebuff':
                emberscar_mark.update( {
                  targetID: 1
                } )
              case 'removedebuff':
                emberscar_mark.update( {
                  targetID: 0
                } )
          case 422277:
            print( '  Devour Essence', slam_count )
            slam_count += 1
            for player, status in emberscar_mark.items():
              if status:
                ignited_essence.update( {
                  player: 0
                } )
