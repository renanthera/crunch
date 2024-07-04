from .helper import *
import wcl

params = {
  'limit': 25000
}

def fight_params_update( self ):
  def entry_match_fn( id ):
    return lambda combatant_info: any( [
      talent.get( 'id' ) == id
      for talent in [
          entry
          for tree in [ 'talentTree', 'talent_tree' ]
          for entry in combatant_info.get( tree, [] )
      ]
    ] )

  players = [
    f"'{player}'"
    for player in wcl.getPlayerNameWith( self.params, entry_match_fn( 125028 ) )
  ]
  player_names = ', '.join( players )
  clause_0 = f"(source.name in ({player_names}))"
  clause_1_id = 450711
  clause_1 = f"(in range from (type='applybuff' and ability.id={clause_1_id} and {clause_0}) to (type='removebuff' and ability.id={clause_1_id} and {clause_0}) end)"
  clause_2_ids = [
    450763, # aspect of harmony damage
    450820, # purified spirit damage
    322507, # celestial brew cast
  ]
  clause_2 = f"(ability.id in ({', '.join((str(x) for x in clause_2_ids))}))"

  clauses = ' or '.join( [
    clause_1,
    clause_2
  ] )
  return {
    'filterExpression': f"{clause_0} and ({clauses})"
  }

def fmt_timestamp( timestamp ):
  timestamp_s = timestamp // 1000
  timestamp_m = timestamp_s // 60
  timestamp_h = timestamp_m // 60
  return f'{timestamp_h%60:02}:{timestamp_m%60:02}:{timestamp_s%60:02}.{timestamp%1000:03}'

def print_events( self, event ):
  if event.get('abilityGameID') not in [ 450763, 450820 ]:
    print(event)

def toggle( self, _ ):
  self.event_data['is_accumulating'] = not self.event_data['is_accumulating']
  if not self.event_data['is_accumulating']:
    self.event_data['value'] = 0

def get_damage( event ):
  return event.get( 'amount', 0 ) + event.get( 'absorbed', 0 ) + event.get( 'overkill', 0 )

def accumulate( self, event ):
  if event.get( 'abilityGameID' ) not in [ 450763, 450820 ] and event.get( 'sourceID' ) != event.get( 'targetID' ):
    print( fmt_timestamp( event.get('timestamp') - self.params['startTime'] ), end='' )
    print(f" {self.event_data['value']}+={get_damage(event)}*0.25 ({get_damage(event)*0.25})")
    print(event)
    self.event_data['value'] += get_damage(event) * 0.25

def p( self, event ):
  def u( n, r, s ):
    print( f"\tE({n}): {r}")
    print( f"\tA({n}): {s}")
    print( f"\tD({n}): {abs(r-s)}")
    print( f"\t%({n}):   {r/s if s != 0 else 'NAN'}")
    print( f"\t%-1({n}): {s/r if r != 0 else 'NAN'}")
  v = self.event_data['value']
  e_v = get_damage(event)
  print( fmt_timestamp( event.get('timestamp') - self.params['startTime'] ) )
  u("Accumulated", v, e_v * 8)
  u("Tick", v/8, e_v)

def spender(report_codes):
  Analyzer(
    report_codes,
    params=params,
    callbacks=[
      {
        'type': ['applybuff', 'removebuff'],
        'abilityGameID': 450711,
        'callback': toggle
      },
      {
        'type': 'damage',
        'callback': accumulate
      },
      {
        'type': 'damage',
        'abilityGameID': 450763,
        'callback': p
      }
    ],
    event_data={
      'is_accumulating': False,
      'value': 0
    },
    fight_params_update=fight_params_update
  )
