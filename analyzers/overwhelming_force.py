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
  source_timestamp: int = 0
  final_amount: int = 0
  final_hit_count: int = 0
  final_timestamp: list[int] = field(default_factory=list)

def sqrt_coeff(target_count):
  if target_count > 5:
    return sqrt(target_count/5) * target_count
  return target_count

def source(analyzer, event):
  source_id = event.get('sourceID', -1)
  ability_game_id = event.get('abilityGameID', -1)
  source_amount = event.get('amount', 0) + event.get('absorbed', 0) + event.get('overkill', 0)
  source_timestamp = event.get('timestamp')
  if source_id in analyzer.event_data['events'].keys():
    analyzer.event_data['events'][source_id].append(Event(source_id, ability_game_id, source_amount, source_timestamp))
  else:
    analyzer.event_data['events'][source_id] = [Event(source_id, ability_game_id, source_amount, source_timestamp)]

def final(analyzer, event):
  source_id = event.get('sourceID', -2)
  if len(analyzer.event_data['events'].get(source_id, [])) == 0:
    return
  update_event = analyzer.event_data['events'][source_id][-1]
  if update_event.source_id != source_id:
    print("something went horribly wrong")
    print(update_event)
    print(event)
    raise SystemExit
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
      # 'filterExpression': f'ability.id in ({", ".join([str(id) for id in ids])})',
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

  nc = 0
  c = 0
  coefficients = []
  for fight in a.data:
    for source_id, events in fight['event_data']['events'].items():
      if nc + c > 0:
        print('report_code:', fight['report_code'], 'fight_id:', fight['fight_id'], 'source_id:', source_id)
        print(f'{c}/{nc} ({round(c/(nc+c)*100,2)}%)')
      nc = 0
      c = 0
      for event in events:
        delta = event.final_timestamp[-1] - event.source_timestamp if len(event.final_timestamp) > 0 else -1
        ratio = event.final_amount / event.source_amount if event.source_amount > 0 else -1
        if ratio > 0.3:
          c += 1
        else:
          nc += 1
        if delta > 0 and ratio > 0 and delta < 100 and event.final_hit_count == 1:
          # print(delta, event.final_hit_count, ratio / sqrt_coeff(event.final_hit_count))
          coefficients.append(ratio)
        # print(event)

  # buckets = [
  #   (i*0.01, len([
  #     v
  #     for v in coefficients
  #     if abs(v-i*0.01) < 0.0099
  #   ]))
  #   for i in range(0,100)
  # ]
  # print()
  # for bucket in buckets:
  #   if bucket[1] > 0:
  #     print(round(bucket[0],2), bucket[1])

  nc = len([v for v in coefficients if v < 0.3])
  c  = len([v for v in coefficients if v > 0.3])

  print('\nTOTAL')
  print(f'{c}/{nc} ({round(c/(nc+c)*100,2)}%)')

  # for fight in a.data:
  #   print(fight['report_code'], fight['fight_id'])
  #   for source_id, events in fight['event_data']['events'].items():
  #     for event in events:
  #       delta = event.final_timestamp[-1] - event.source_timestamp if len(event.final_timestamp) > 0 else -1
  #       ratio = event.final_amount / event.source_amount if event.source_amount > 0 else -1
  #       if ratio > 0.4 and delta > 0 and ratio > 0 and delta < 100 and event.final_hit_count == 1:
  #         print(ratio, event)
  # import matplotlib.pyplot as plt
  # plt.style.use('dark_background')
  # plt.hist(coefficients)
  # plt.show()
