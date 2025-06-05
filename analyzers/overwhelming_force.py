from .helper import *
from dataclasses import dataclass, field
from math import sqrt
import wcl

# 2$Off$#244F4B$damage$-1$0.0.0.Any$0.0.0.Any$true$0.0.0.Any$true$185099|205523|100780|452333|386959
ids = [
  185099,
  205523,
  100780,
  452333,
  # 386959
]

@dataclass
class Event:
  source_id: int = 0
  ability_game_id: int = 0
  source_amount: int = 0
  source_is_crit: bool = False
  source_timestamp: int = 0
  final_amount: int = 0
  final_hit_count: int = 0
  final_is_crit: bool = False
  final_timestamp: list[int] = field(default_factory=list)

  report_code: str = ""
  fight_id: int = 0
  ratio: float = 0.0
  timestamp_delta: int = 0

  def post_init(self, report_code, fight_id):
    self.report_code = report_code
    self.fight_id = fight_id
    self.ratio = self.final_amount / self.source_amount
    if (self.final_timestamp):
      self.timestamp_delta = self.final_timestamp[-1] - self.source_timestamp
    self.final_is_crit = self.ratio > 0.3

    return self.timestamp_delta < 100

def sqrt_coeff(target_count):
  if target_count > 5:
    return sqrt(target_count/5) * target_count
  return target_count

def source(analyzer, event):
  source_id = event.get('sourceID', -1)
  ability_game_id = event.get('abilityGameID', -1)
  source_amount = event.get('amount', 0) + event.get('absorbed', 0) + event.get('overkill', 0)
  source_timestamp = event.get('timestamp')
  is_crit = event.get('hitType', -1) == 2
  if source_id in analyzer.event_data['events'].keys():
    analyzer.event_data['events'][source_id].append(Event(source_id, ability_game_id, source_amount, is_crit, source_timestamp))
  else:
    analyzer.event_data['events'][source_id] = [Event(source_id, ability_game_id, source_amount, is_crit, source_timestamp)]

def final(analyzer, event):
  source_id = event.get('sourceID', -2)
  if not analyzer.event_data['events'].get(source_id, []):
    return
  update_event = analyzer.event_data['events'][source_id][-1]
  if update_event.source_id != source_id:
    assert(False, "something went horribly wrong", update_event, event)
  update_event.final_amount += event.get('amount', 0) + event.get('absorbed', 0) + event.get('overkill', 0)
  update_event.final_hit_count += 1
  update_event.final_timestamp.append(event.get('timestamp'))

def fight_params_update( self ):
  def entry_match_fn( id ):
    return lambda combatant_info: any( [
      talent.get( 'id' ) == id
      for talent in [
          entry
          for tree in [ 'talentTree', 'talent_tree', 'pvpTalents' ]
          for entry in combatant_info.get( tree, [] )
      ]
    ] )

  players = [
    f"'{player}'"
    for player in wcl.getPlayerNameWith( self.params, entry_match_fn( 125029 ) )
  ]
  player_names = ', '.join( players )
  clause_0 = f"(source.name in ({player_names}))"

  clause_1 = f"(ability.id in ({', '.join((str(x) for x in ids))}))"

  return {
    'filterExpression': f"{clause_0} and {clause_1}"
  }

def coefficient(report_codes):
  import json
  a = Analyzer(
    report_codes,
    params={
      'limit': 25000,
      'filterExpression': "type='combatantinfo'",
      'encounterID': 3013
    },
    callbacks=[
      {
        'any': False,
        'callback': lambda _, e: print(json.dumps(e, indent=2))
      },
      {
        'type': 'damage',
        'abilityGameID': [
          205523,
          100780,
          185099
        ],
        'callback': source
      },
      {
        'abilityGameID': 452333,
        'callback': final
      }
    ],
    event_data={
      'events': dict(),
    },
    fight_params_update=fight_params_update
  )

  d1 = [1 + v * 0.08 for v in range(0, 5)]
  d2 = [1.00, 1.20]
  m1 = [1.00, 2.00]

  coeff = [
    round(0.25 / a / b * c, 3)
    for a in d1
    for b in d2
    for c in m1
  ]
  coeff_2 = [
    f'{a:.2f}\t{b:.2f}\t{c:.2f}'
    for a in d1
    for b in d2
    for c in m1
  ]

  # coefficient and source map
  # print(json.dumps(sorted(zip(coeff, coeff_2), key=lambda v: v[0]), indent=2))

  flat_events = [
    event
    for fight in a.data
    for events in fight['event_data']['events'].values()
    for event in events
    if event.post_init(fight['report_code'], fight['fight_id'])
  ]

  crits = [event for event in flat_events if event.final_is_crit]
  noncrits = [event for event in flat_events if not event.final_is_crit]
  doublecrits = [event for event in flat_events if event.source_is_crit and event.final_is_crit]
  crits_by_source = {185099: 0, 205523: 0, 100780: 0}
  hits_by_source = {185099: 0, 205523: 0, 100780: 0}
  crit_count = len(crits)
  noncrit_count = len(noncrits)
  crit_chance = round(crit_count/(crit_count+noncrit_count)*100, 2)
  doublecrit_count = len(doublecrits)
  coefficient_count = {k: 0 for k in sorted(coeff)}
  errors = [event for event in flat_events if round(event.ratio, 3) not in coeff and event.ratio > 0]
  crit_errors = [event for event in errors if event.final_is_crit]
  noncrit_errors = [event for event in errors if not event.final_is_crit]
  for event in flat_events:
    rratio = round(event.ratio, 3)
    if rratio in coeff and event.ratio > 0:
      coefficient_count[rratio] += 1
    if event.final_is_crit:
      crits_by_source[event.ability_game_id] += 1
    hits_by_source[event.ability_game_id] += 1
  print(f"errors:")
  for error in errors:
    print(error)
  print()
  print(f"error counts - c: {len(crit_errors)}, nc: {len(noncrit_errors)}, t: {len(errors)}")
  print(f"crits: {crit_count}/{crit_count+noncrit_count} ({crit_chance}%)")
  print(f"doublecrits: {doublecrit_count}")
  print(f"largest coefficient: {max(flat_events, key=lambda e: e.ratio)}")
  print(f"hits by source: {hits_by_source}")
  print(f"crits by source: {crits_by_source}")
  print(f"crit chance by source: {({k: round(crits_by_source[k]/hits_by_source[k]*100,2) for k in crits_by_source.keys()})}")
  print("hits by ratio:\nratio\tcount\test\t(/woo\t/coale\t*crit)")
  for coeff_pair in sorted(zip(coeff, coeff_2), key=lambda v: v[0]):
    print(f"{coeff_pair[0]}\t{coefficient_count[coeff_pair[0]]}\t{round(coefficient_count[coeff_pair[0]]*crit_chance/100)}\t({coeff_pair[1]})")
