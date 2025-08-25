from .helper import *
from wcl import getPlayerFromID, getPlayers
import wcl

import matplotlib.pyplot as plot
import json
from copy import deepcopy

# NOTES:
# Not all seeds spawned from Flaming Germination spawn at the same time.

TEXT_REPORT = True
GRAPHICAL_REPORT = True
GRAPHICAL_REPORT_2 = True


def update_pos(event, event_data):
  target_id = event.get('targetID')
  x = event.get('x')
  y = event.get('y')
  if target_id and x and y and target_id in event_data['entities'].keys():
    event_data[ 'entities' ][ target_id ][ 'position' ].update( {
      'x': x,
      'y': y,
      'last_update': event.get( 'timestamp' )
    } )  # yapf: disable


def relative_pos(pos1, pos2):
  return {'x': pos1['x'] - pos2['x'], 'y': pos1['y'] - pos2['y']}


def soak_seed(event, event_data):
  target_id = event.get('targetID')
  timestamp = event.get('timestamp')
  last_boss_cast = event_data['last_boss_cast']
  target_data = event_data['entities'][target_id]
  target_position = target_data['position']
  boss_position = event_data['boss_info']['position']
  previous_soak = target_data['soaks'][-1:]
  previous_soak_timestamp = (
    len(previous_soak) > 0 and previous_soak[0]['timestamp'] or -1e10
  )
  soak_info = {
    'target_id': target_id,
    'timestamp': timestamp,
    'last_boss_cast': last_boss_cast,
    'target_position': deepcopy(target_position),
    'boss_position': deepcopy(boss_position),
    'double_soak': previous_soak_timestamp >= last_boss_cast and True or False,
    'cast_count': event_data['cast_count'],
  }
  event_data['entities'][target_id].update({'exists': True})
  event_data['entities'][target_id]['soaks'].append(soak_info)

  if TEXT_REPORT:
    target_name = target_data['name']
    relative = relative_pos(target_position, boss_position)
    delta = timestamp - last_boss_cast
    print(f'\t{target_name} soaked at {relative} after {delta} milliseconds')
    if soak_info['double_soak']:
      print(f'\t!!!!{target_name} double soaked!!!!')


def boss_cast(event, event_data):
  event_data['last_boss_cast'] = event.get('timestamp')
  event_data['boss_info']['exists'] = True
  event_data['cast_count'] += 1
  for player_info in event_data['entities'].values():
    if player_info['alive']:
      player_info.update({'soak_candidate': player_info['soak_candidate'] + 1})

  if TEXT_REPORT:
    caster_id = event.get('targetID')
    caster_name = event_data['boss_info']['name']
    position = event_data['entities'][caster_id]['position']
    print(f'{caster_name} casts at {position}')


def death(event, event_data):
  target_id = event.get('targetID')
  if target_id in event_data['entities']:
    event_data['entities'][target_id].update({'alive': False, 'exists': True})


def initialize_objects(_, event_data):
  entities = wcl.getMasterData(event_data['params'])
  event_data['entities'] = {
    entity.get('id'): {
      'exists': False,
      'name': entity.get('name'),
      'type': entity.get('type'),
      'subtype': entity.get('subType'),
      'alive': True,
      'soak_candidate': 0,
      'soaks': [],
      'position': {'x': 0, 'y': 0, 'last_update': -1},
    }
    for entity in entities
    if entity.get('type') in ['NPC', 'Player']
  }

  event_data.update( {
    'boss_info': entity
    for entity in event_data[ 'entities' ].values()
    if entity[ 'name' ] == "Tindral Sageswift"
  } )  # yapf: disable


def flaming_germination(reportCodes, groups):
  event_data_base = {
    'entities': {},
    'boss_info': {},
    'last_boss_cast': 0,
    'cast_count': 0,
  }
  data = report_code_to_events(
    reportCodes,
    {
      'limit': 25000,
      'includeResources': True,
      'filterExpression': "type in ('damage', 'resourcechange', 'cast', 'heal', 'drain', 'encounterstart', 'death')",
    },
    lambda fight: fight.get('name') == 'Tindral Sageswift, Seer of the Flame',
    event_data_base,
    [
      {'type': 'encounterstart', 'callback': initialize_objects},
      {'type': 'damage', 'abilityGameID': 430584, 'callback': soak_seed},
      {'type': 'cast', 'abilityGameID': 423265, 'callback': boss_cast},
      {'type': 'death', 'callback': death},
      {'any': True, 'callback': update_pos},
    ],
  )

  def get_value_in_data(entry, target_id, data):
    return [
      value.get(entry)
      for r in data.values()
      for f in r.values()
      for child_id, value in f['entities'].items()
      if child_id == target_id
    ]

  def reduce_identical_entries(entry, target_id, data):
    entries = get_value_in_data(entry, target_id, data)
    first = entries[0]
    if all([name == first for name in entries]):
      return first
    return entries

  entities = {
    target_id: {
      'exists': reduce_identical_entries('exists', target_id, data),
      'name': reduce_identical_entries('name', target_id, data),
      'soak_candidate': sum(get_value_in_data('soak_candidate', target_id, data)),
      'soaks': [
        soak
        for soaks in get_value_in_data('soaks', target_id, data)
        for soak in soaks
        # if soak.get( 'cast_count' ) > 3
      ],
      'soak_count': None,
      'double_soak_count': None,
    }
    for report_data in data.values()
    for fight_data in report_data.values()
    for target_id in fight_data['entities'].keys()
    if any(get_value_in_data('exists', target_id, data))
  }

  for target_data in entities.values():
    target_data.update(
      {
        'soak_count': len(
          [soak for soak in target_data['soaks'] if not soak.get('double_soak')]
        ),
        'double_soak_count': len(
          [soak for soak in target_data['soaks'] if soak.get('double_soak')]
        ),
      }
    )
    filtered_latencies = [
      soak.get('timestamp') - soak.get('last_boss_cast')
      for soak in target_data['soaks']
      if not soak.get('double_soak')
    ]

    if len(filtered_latencies) != 0:
      target_data.update(
        {'mean_latency': sum(filtered_latencies) / len(filtered_latencies)}
      )

  if TEXT_REPORT:
    out = {
      target_id: {
        key: value
        for key, value in player.items()
        if key
        in ['name', 'soak_candidate', 'soak_count', 'double_soak_count', 'mean_latency']
      }
      for target_id, player in entities.items()
    }
    print(json.dumps(out, indent=2))

  if GRAPHICAL_REPORT or GRAPHICAL_REPORT_2:

    def get_group_id(target_name, groups):
      for g_id, group in enumerate(groups):
        if target_name in group:
          return g_id
      return -1

    # Red Green Blue Cyan Magenta Yellow blacK White
    color_map = 'rgbcmy'
    # color_map = 'kgkkmk'
    soaks = [
      {
        'x': position['x'],
        'y': position['y'],
        'delta': soak.get('timestamp') - soak.get('last_boss_cast'),
        'group_color': color_map[get_group_id(player_data['name'], groups)],
      }
      for player_data in entities.values()
      for soak in player_data['soaks']
      for position in [
        relative_pos(soak.get('target_position'), soak.get('boss_position'))
      ]
    ]
    soaks.append(
      {
        'x': 0,
        'y': 0,
        'delta': min([soak.get('delta') for soak in soaks]),  # pyright: ignore
        'group_color': 'white',
      }
    )

  if GRAPHICAL_REPORT:
    plot.style.use('dark_background')
    plot.scatter(
      *[[s.get(l) for s in soaks] for l in ['x', 'y']],  # pyright: ignore
      c=[s.get('delta') for s in soaks],  # pyright: ignore
      cmap='jet',
    )
    plot.colorbar()
    plot.show()

  if GRAPHICAL_REPORT_2:
    plot.style.use('dark_background')
    plot.scatter(
      *[[s.get(l) for s in soaks] for l in ['x', 'y']],  # pyright: ignore
      c=[s.get('group_color') for s in soaks],  # pyright: ignore
    )
    plot.show()


def flaming_germination_2(report_codes, groups):
  t = Analyzer(
    report_codes,
    groups=groups,
    callbacks=[
      {'any': True, 'callback': lambda s, e: s.event_data.update({100: e})},
    ],
    params={
      'limit': 25000,
      'includeResources': True,
      'filterExpression': "type in ('damage', 'resourcechange', 'cast', 'heal', 'drain', 'encounterstart', 'death')",
    },
    fight_filter=lambda _, f: f.get('name')
    in ['Tindral Sageswift, Seer of the Flame', 'Tindral Sageswift'],
  )
  print(json.dumps(t.data, indent=2))
