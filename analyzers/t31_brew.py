import wcl
from collections import defaultdict

import json

__all__ = [ 'proc', 'guard' ]

def guard( reportCodes ):
  pass

def proc( reportCodes ):
  all_ratios = []

  whitelist_trigger_4p = [
    1,      # melee hit
    185099, # rising sun kick hit
    115129, # expel harm hit
    132467, # chi wave hit
    # chi burst hit
    # 196608, # eye of the tiger dot
    391400, # resonant fists hit
    121253, # keg smash hit
    148187, # rushing jade wind hit
            # special delivery hit
    115181, # breath of fire hit
    # 123725, # breath of fire dot
    386959, # charred passions hit
    387621, # dragonfire brew hit
    # 325217, # bonedust brew hit
    325153, # exploding keg hit
    388867, # exploding keg proc
    # press the advantage
    # 393786, # chi surge dot
    205523, # blackout kick hit
    # 117952, # crackling jade lightning dot
    107270, # spinning crane kick hit
    100780, # tiger palm hit
    322109, # touch of death hit
    389541, # claw of the white tiger hit
    1,      # niuzao melee hit
    227291, # niuzao stomp hit
  ]

  whitelist_trigger_2p = [
    115181, # breath of fire hit
    123725, # breath of fire dot
  ]

  for reportCode in reportCodes:
    print( '===================================' )
    print( 'report code:', reportCode )
    wcl.getPointsSpent()
    print( '===================================' )

    params = {
      'code': reportCode,
      'startTime': 0,
      'endTime': 1e30,
      'limit': 10000
    } # yapf: disable

    fights = [
      fight for fight in wcl.getFights( params )
      if fight.get( 'endTime' ) - fight.get( 'startTime' ) > 1000 * 60 * 3
    ]

    for fight in range( len( fights ) ):
      # print( fight + 1 )

      params.update( {
        'startTime': fights[ fight ].get( 'startTime' ),
        'endTime': fights[ fight ].get( 'endTime' )
      } )

      players = wcl.getPlayerDetails( params ).get( 'tanks' )
      candidates = [
        player for player in players
        if any( [ spec.get( 'spec' ) == 'Brewmaster' for spec in player.get( 'specs' ) ] )
      ]

      for candidate in candidates:
        # print( candidate.get( 'name' ) )

        params.update( {
          'filterExpression':
          f"source.name='{candidate.get('name')}' and ((type in ('applydebuff', 'removedebuff') and ability.id=123725) or (type = 'damage'))"
        } )

        events = wcl.getEvents( params )
        assert events is not None

        debuff_hits = defaultdict( int )
        total_hits = defaultdict( int )
        active_targets = {}
        for event in events:
          ident = str( event.get( 'targetID' ) ) + '-' + str( event.get( 'targetInstance', 0 ) )
          spell_id = event.get( 'abilityGameID' )
          match event.get( 'type' ):
            case 'applydebuff':
              if spell_id == 123725:
                active_targets.update( {
                  ident: True
                } )
            case 'removedebuff':
              if spell_id == 123725:
                active_targets.update( {
                  ident: False
                } )
            case 'refreshdebuff':
              pass
            case 'damage':
              total_hits[ spell_id ] += 1
              if active_targets.get( ident ):
                debuff_hits[ spell_id ] += 1
            case _:
              pass
        triggers_total = total_hits.get( 425299 )
        assert triggers_total is not None and triggers_total > 0
        triggers_2p = sum( [
          value for key,
          value in total_hits.items() if key in whitelist_trigger_2p
        ] )
        triggers_4p = triggers_total - triggers_2p
        candidates_4p = sum( [
          value for key,
          value in debuff_hits.items() if key in whitelist_trigger_4p
        ] )
        assert candidates_4p is not None and candidates_4p > 0

        ratio = triggers_4p / candidates_4p
        all_ratios.append( ratio )
        # print( triggers_total, triggers_2p, triggers_4p, candidates_4p )
        # print( ratio )
  print( json.dumps(all_ratios, indent=2))
  print( sum( all_ratios ) / len( all_ratios ) )

  # print( json.dumps( candidates, indent=2 ) )
