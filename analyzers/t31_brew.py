import wcl
from collections import defaultdict

import json

__all__ = [ 'proc', 'guard' ]

def guard( reportCodes ):
  pass

def proc( reportCodes ):

  whitelist_trigger_4p = [
    1,      # melee hit
    185099, # rising sun kick hit
    115129, # expel harm hit
    132467, # chi wave hit
    148135, # chi burst hit
    # 196608, # eye of the tiger dot
    391400, # resonant fists hit
    121253, # keg smash hit
    148187, # rushing jade wind hit
    196733, # special delivery hit
    115181, # breath of fire hit
    # 123725, # breath of fire dot
    386959, # charred passions hit
    387621, # dragonfire brew hit
    # 325217, # bonedust brew hit
    325153, # exploding keg hit
    388867, # exploding keg proc
    418360, # press the advantage
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

  all_ratios = []
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
      if fight.get( 'endTime' ) - fight.get( 'startTime' ) > 1000 * 60 * 1.5
    ]

    for fight in range( len( fights ) ):
      # print( fight + 1 )

      params.update( {
        'startTime': fights[ fight ].get( 'startTime' ),
        'endTime': fights[ fight ].get( 'endTime' )
      } )

      players = wcl.getPlayerDetails( params ).get( 'tanks' )
      # assert players is not None, f'No players found for {reportCode} -> {fight}'
      if players is None:
        continue
      candidates = [
        player for player in players
        if any( [ spec.get( 'spec' ) == 'Brewmaster' for spec in player.get( 'specs' ) ] )
      ]

      for candidate in candidates:
        # print( candidate.get( 'name' ) )

        params.update( {
          'filterExpression':
          f"source.name in ('{candidate.get('name')}', 'White Tiger Statue', 'Niuzao') and ((type in ('applydebuff', 'removedebuff') and ability.id=123725) or (type = 'damage'))"
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

        data = {
          'ratio': triggers_4p / candidates_4p,
          'bdb': total_hits.get( 325217,
                                 0 ) / sum( total_hits.values() )
        }
        if not any( [ v == 0 for v in data.values() ] ):
          all_ratios.append( data )
        procs_by_source = defaultdict( int )
        vals = [ 0.4, 0.15 ]
        deltas = []
        occurred = False
        hist_ratio = 0
        factor_buckets = {} # yapf: disable
        for event_id in range( len( events ) ):
          event = events[ event_id ]
          amount = event.get( 'unmitigatedAmount', 0 )
          if event.get( 'abilityGameID' ) == 425299:
            amount_2 = event.get( 'amount', 0 ) + event.get( 'absorbed', 0 ) + event.get( 'overkill', 0 ) + event.get( 'mitigated', 0 ) # yapf: disable
            factor = round( amount_2 / amount, 2 )
            factor_buckets.update( {
              factor: factor_buckets.get( factor,
                                          0 ) + 1
            } )
            # factor_buckets[factor] += 1
            if amount != amount_2 and not occurred:
              occurred = True
              hist_ratio = amount_2 / amount
              # print( f'{reportCode} -> {fight} has incorrect values: {amount_2 / amount}' )
              # if amount_2 / amount > 1.13:
              #   print( event )
            for backtrack_event_id in range( event_id, 1, -1 ):
              backtrack_event = events[ backtrack_event_id ]
              if backtrack_event.get( 'type' ) != 'damage':
                continue
              backtrack_amount = backtrack_event.get( 'amount', 0 ) + backtrack_event.get( 'absorbed', 0 ) + backtrack_event.get( 'overkill', 0 ) # yapf: disable
              assert backtrack_amount > 0, 'Bad backtrack amount.' + str( backtrack_event )
              ratio = amount / backtrack_amount
              check_vals = [ abs( ratio - v ) <= 1e-3 for v in vals ]
              if any( check_vals ):
                id = str( backtrack_event.get( 'abilityGameID' ) ) + '-' + str( ( check_vals.index( True ) + 1 ) * 2 ) + 'p' # yapf: disable
                if ( check_vals.index( True ) == 0
                     and backtrack_event.get( 'abilityGameID' ) not in whitelist_trigger_2p
                     or check_vals.index( True ) == 1 and backtrack_event.get( 'abilityGameID' )
                     not in whitelist_trigger_4p ) and not backtrack_event.get( 'used' ):
                  pass
                  # print(f'detected {(check_vals.index(True)+1)*2}p but not on whitelist, skipping...')
                  # print(f'failed on id: {backtrack_event.get("abilityGameID")}, amount: {backtrack_amount} -> {amount}, ratio: {ratio}, delta: {abs(ratio-vals[check_vals.index(True)])}, triggered by: {(check_vals.index(True)+1)*2}p')
                else:
                  # print(f'id: {backtrack_event.get("abilityGameID")}, amount: {backtrack_amount} -> {amount}, ratio: {ratio}, delta: {abs(ratio-vals[check_vals.index(True)])}, triggered by: {(check_vals.index(True)+1)*2}p')
                  backtrack_event.update( {
                    'used': True
                  } )
                  deltas.append( abs( ratio - vals[ check_vals.index( True ) ] ) )
                  procs_by_source[ id ] += 1
                break
              else:
                pass
                # print(f'NO MATCHES DETECTED FOR ID {event_id} and {backtrack_event_id}')
                # print(f'failed on id: {backtrack_event.get("abilityGameID")}, amount: {backtrack_amount} -> {amount}, ratio: {ratio}')
        data.update( {
          'procs_by_source': procs_by_source, # pyright: ignore
          'factor_buckets': factor_buckets
        } )
        # print(json.dumps(data, indent=2))
  # for k in all_ratios[ 0 ].keys():
  #   print( k, sum( [ f.get( k, 0 ) for f in all_ratios if not isinstance(f.get(k), dict) ] ) / len( all_ratios ) )

  # for k in all_ratios:
  #   print(k.get('ratio'))

  merged_factor_buckets = {}
  for entry in all_ratios:
    for bucket, amount in entry.get( 'factor_buckets' ).items():
      merged_factor_buckets.update( {
        bucket: amount + merged_factor_buckets.get( bucket,
                                                    0 )
      } )

  print( json.dumps( merged_factor_buckets, indent=2 ) )
