from .helper import *
from copy import deepcopy
import wcl
import clipboard
from collections import defaultdict

# triggers = [ 450521, 450526, 450531  ]
triggers = [
  # 1, # melee attack
  418360,  # pta melee strike
  100780,  # tiger palm
  452333,  # overwhelming force
  # cta niuzao melee <- include pets
  # invoke niuzao melee <- include pets
  121253,  # keg smash
  205523,  # blackout kick
  185099,  # rising sun kick
  117952,  # cjl
  107270,  # sck
  148135,  # chi burst damage
  115181,  # breath of fire
  123725,  # bof dot
  325153,  # exploding keg
  388867,  # ek bonus
  148187,  # rjw
  1242373,  # wwto stomp
  196733,  # special delivery
  1239442,  # harmonic surge damage
  1239443,  # harmonic surge heal
  322101,  # expel harm heal
  116670,  # vivify
  130654,  # chi burst heal
  455179,  # elixir of determination
  451253,  # mantra of purity
]
force = [1241059, 322507, 125008]
success = [1239483]
talent = [125039, 124865]
items = [237673, 237671, 237676, 237672, 237674]
DBG = False


def fight_params_update(self):
  def entry_match_fn(id, items):
    return (
      lambda combatant_info: [
        talent.get('id') in id
        for talent in [
          entry
          for tree in ['talentTree', 'talent_tree']
          for entry in combatant_info.get(tree, [])
        ]
      ].count(True)
      == len(talent)
      and [item.get('id') in items for item in combatant_info.get('gear', [])].count(
        True
      )
      >= 4
    )

  players = set(
    f'{player}'
    for player in wcl.getPlayerNameWith(self.params, entry_match_fn(talent, items))
  )

  player_names = ', '.join([f"'{p}'" for p in players])

  if len(players):
    player_ids = set(wcl.getPlayerWith(self.params, entry_match_fn(talent, items)))
    self.params.update(
      {'filterExpression': f"target.name in ({player_names}) and type = 'death'"}
    )
    deaths = wcl.getEvents(self.params)
    if any([death.get('targetID') in player_ids for death in deaths]):
      print('SOURCE DIED')
      self.event_data['deaths'] = True
  else:
    self.event_data['deaths'] = False

  # md = wcl.getMasterData( self.params )

  # import json
  # print(json.dumps(md,indent=2))
  # for actor in md:
  #   if actor.get('name') in players:
  #     aliases = set(actor.get('name'))
  #     for b_actor in md:
  #       if b_actor.get('petOwner') == actor.get('id'):
  #         aliases.add(b_actor.get('id'))
  #         if "'" not in b_actor.get('name'):
  #           players.add(b_actor.get('name'))
  #     if len(aliases):
  #       self.event_data['source_id_aliases'].update({actor.get('id'): aliases})

  players = sorted(players)
  player_names = ', '.join([f"'{p}'" for p in players])
  clause_0 = f'(source.name in ({player_names}))'

  clause_2_ids = [*triggers, *success, *force]
  clause_2 = f'ability.id in ({", ".join((str(x) for x in clause_2_ids))})'

  clauses = ' or '.join([clause_2])
  if self.event_data['deaths']:
    return {'filterExpression': 'source.id=10000000'}
  v = {'filterExpression': f'{clause_0} and ({clauses})'}
  # self.params.update(v)
  return v


def fmt_timestamp(timestamp):
  timestamp_s = timestamp // 1000
  timestamp_m = timestamp_s // 60
  timestamp_h = timestamp_m // 60
  return f'{timestamp_h % 60:02}:{timestamp_m % 60:02}:{timestamp_s % 60:02}.{timestamp % 1000:03}'


def check_icd(icds, event, icd):
  # print(icds.get(event.get('abilityGameID')))
  # print(event.get('timestamp'))
  # print(event.get('timestamp')-icds.get(event.get('abilityGameID'),0))
  if icds.get(event.get('abilityGameID'), 0) == 0:
    icds[event.get('abilityGameID')] = event.get('timestamp')
    return True
  if icds.get(event.get('abilityGameID')) + icd <= event.get('timestamp'):
    icds[event.get('abilityGameID')] = event.get('timestamp')
    return True
  return False


def cb(self, event):
  if self.event_data['deaths']:
    return

  if event.get('abilityGameID') == 455179:
    return

  timestamp = event.get('timestamp') - self.params.get('startTime')
  time_bucket = False
  icd = 5

  source_id = event.get('sourceID')
  # if event.get('sourceID') in self.event_data['source_id_aliases'].keys():
  #   source_id = event.get('sourceID')
  # for key, val in self.event_data['source_id_aliases'].items():
  #   if event.get('sourceID') in val:
  #     source_id = key
  #     break
  # if source_id == 0:
  #   print(event.get('sourceID'))
  #   print(self.event_data['source_id_aliases'])
  #   print(self.event_data['deaths'])
  #   print(event)
  assert source_id != 0
  if source_id not in self.event_data['info'].keys():
    self.event_data['info'][source_id] = deepcopy(self.event_data['info_base'])

  # nice friendly ref
  info = self.event_data['info'][source_id]

  # filter for icd
  if (
    icd
    and event.get('abilityGameID') in triggers
    and event.get('abilityGameID') not in [148135, 130654]
    and event.get('type') in ['damage', 'absorbed', 'heal', 'applybuff', 'refreshbuff']
  ):
    if not check_icd(info['icd'], event, icd):
      return

  # if icd and event.get('abilityGameID') in triggers:
  #   if ( info['last_trigger_attempt'] != 0 and info['last_trigger_attempt'] > event.get('timestamp') - icd ):
  #     return

  # if event bucketing, increment index
  if (
    event.get('abilityGameID') in triggers
    and not time_bucket
    and event.get('type') in ['damage', 'absorbed', 'heal', 'applybuff', 'refreshbuff']
  ):
    info['count_since_last'] += 1

  # calculate index for time bucketing and event bucketing
  index = 0
  if time_bucket:
    index = (event.get('timestamp') - info['count_since_last']) // 1000
  else:
    index = info['count_since_last']

  if event.get('abilityGameID') in success and event.get('type') in [
    'applybuffstack',
    'removebuffstack',
  ]:
    info['potential_energy_stacks'] = event.get('stack')
  if event.get('abilityGameID') in success and event.get('type') == 'applybuff':
    info['potential_energy_stacks'] = 1
  if event.get('abilityGameID') in success and event.get('type') == 'removebuff':
    info['potential_energy_stacks'] = 0

  # print(time_bucket,index)
  if event.get('abilityGameID') in success:
    if event.get('type') in ['applybuff', 'applybuffstack'] or (
      event.get('type') == 'refreshbuff'
      and info['potential_energy_stacks'] == 6
      and info['count_since_last'] > 0
    ):
      if DBG:
        print(
          'SUCCESS',
          fmt_timestamp(timestamp),
          f'({fmt_timestamp(event.get("timestamp") - info["last_success"])})',
          event.get('timestamp') - info['last_success'] >= icd,
        )
      if index == 0 and DBG:
        print('???????????????', event.get('abilityGameID'))
      if time_bucket:
        info['count_since_last'] = event.get('timestamp')
      else:
        info['count_since_last_backup'] = info['count_since_last']
        info['count_since_last'] = 0
      info['last_success'] = event.get('timestamp')
      info['success_timestamps'].append(event.get('timestamp'))
      info['data'][index]['successful'] += 1

  if event.get('abilityGameID') in force and event.get('type') == 'cast':
    if DBG:
      print(
        'FORCE  ',
        fmt_timestamp(timestamp),
        f'({fmt_timestamp(event.get("timestamp") - info["last_trigger_attempt"])})',
        event.get('timestamp') - info['last_trigger_attempt'] >= icd,
      )
    info['count_since_last'] = info['count_since_last_backup']
    index = 0
    if time_bucket:
      index = (event.get('timestamp') - info['count_since_last']) // 1000
    else:
      index = info['count_since_last']
    info['success_timestamps'].pop()
    info['data'][index]['successful'] -= 1

  if info['count_since_last'] == 0:
    return

  if event.get('abilityGameID') in triggers and event.get('type') in [
    'damage',
    'absorbed',
    'heal',
    'applybuff',
    'refreshbuff',
  ]:
    if DBG:
      print(
        'ATTEMPT',
        fmt_timestamp(timestamp),
        f'({fmt_timestamp(event.get("timestamp") - info["last_trigger_attempt"])})',
        event.get('timestamp') - info['last_trigger_attempt'] >= icd,
        event.get('abilityGameID'),
        index,
      )
    info['data'][index]['failed'] += 1
    info['last_trigger_attempt'] = event.get('timestamp')


fingerprints = []


def _fight_filter(self):
  def keyequal(key, event_pair):
    return event_pair[0].get(key) == event_pair[1].get(key)

  param = deepcopy(self.params)
  param.update(
    {'limit': 5, 'filterExpression': "type not in ('dungeonstart', 'combatantinfo')"}
  )
  fingerprint = wcl.getEventsNoPagination(param)
  if any(
    [
      keyequal('type', e) and keyequal('amount', e) and keyequal('abilityGameID', e)
      for f in fingerprints
      for e in zip(fingerprint, f)
    ]
  ):
    return False
  fingerprints.append(fingerprint)
  return True


def _postprocess(self):
  o = {}
  for _, data in self.event_data['info'].items():
    for index in data['data']:
      o.setdefault(index['index'], {'SUCCESS': 0, 'FAIL': 0})
      o[index['index']]['SUCCESS'] += index['successful']
      o[index['index']]['FAIL'] += index['failed']

  l = [
    f'{key} {value["SUCCESS"]} {value["FAIL"]}'
    for key, value in o.items()
    if value['SUCCESS'] or value['FAIL']
  ]

  # raise SystemExit
  if len(l):
    print(fmt_timestamp(self.params.get('endTime') - self.params.get('startTime')))
    l = [self.params.get('code') + ', ' + str(self.fight_id), 'raw data'] + l
    clipboard.copy('\n'.join(l))
    input()


def probability_at_count(report_codes, **params):
  t = Analyzer(
    report_codes,
    params={'limit': 25000, 'filterExpression': "type='combatantinfo'"},
    callbacks=[
      {
        'type': [
          'applybuff',
          'applybuffstack',
          'removebuffstack',
          'removebuff',
          'refreshbuff',
          'cast',
          'damage',
          'absorbed',
          'heal',
        ],
        'abilityGameID': [*triggers, *success, *force],
        'callback': cb,
      }
    ],
    event_data={
      'blob': params,
      'info_base': {
        'data': [{'index': k, 'failed': 0, 'successful': 0} for k in range(0, 1000)],
        'icd': defaultdict(int),
        'count_since_last': 0,
        'count_since_last_backup': 0,
        'last_trigger_attempt': 0,
        'last_success': 0,
        'potential_energy_stacks': 0,
        'success_timestamps': [],
      },
      'deaths': False,
      'source_id_aliases': {},
      'info': {},
    },
    fight_params_update=fight_params_update,
    postprocess=_postprocess,
    # fight_filter=_fight_filter
  )

  o = {}
  # timestamps = []
  for fight in t.data:
    for _, data in fight['event_data']['info'].items():
      # timestamps.append(data['success_timestamps'])
      for index in data['data']:
        o.setdefault(index['index'], {'SUCCESS': 0, 'FAIL': 0})
        o[index['index']]['SUCCESS'] += index['successful']
        o[index['index']]['FAIL'] += index['failed']

  # for t in timestamps:
  #   print(min([
  #     t[i+1] - t[i]
  #     for i in range(len(t)-1)
  #   ]))

  l = [(key, value['SUCCESS'], value['FAIL']) for key, value in o.items()]

  x = [v[0] for v in l if (v[1] or v[2])]

  y = [v[1] for v in l if (v[1] or v[2])]

  z = [v[2] for v in l if (v[1] or v[2])]

  p = [y[i] / (y[i] + z[i]) for i in range(len(z))]
  # print(x)
  # print(p)
  # print([sum(p[index:]) for index in range(len(x))])

  # import matplotlib.pyplot as plt
  # plt.style.use('dark_background')
  # _, ax = plt.subplots(2,3)
  # ax[0, 0].set_xlabel('number of consecutive failures')
  # ax[0, 0].set_ylabel('success')
  # # ax[0, 0].scatter(x, y)
  # ax[0, 0].scatter(x, [sum(y[:k]) for k in range(len(x))])
  # # ax[0, 0].scatter(x, [sum(y[:k])/sum(y) for k in range(len(x))])
  # r = x
  # s = [sum(y[:k])/sum(y) for k in range(len(x))]
  # # for k in range(len(r)):
  # #   print(s[k])
  # #   # print(f'{r[k]}\t{s[k]}')
  # ax[0, 1].set_xlabel('number of consecutive failures')
  # ax[0, 1].set_ylabel('fail')
  # ax[0, 1].scatter(x, z)
  # ax[0, 2].set_xlabel('number of consecutive failures')
  # ax[0, 2].set_ylabel('P(X=x)')
  # ax[0, 2].scatter(x, p)
  # ax[1, 0].set_xlabel('number of consecutive failures')
  # ax[1, 0].set_ylabel('P(X>=x)')
  # ax[1, 0].scatter(x, [sum(p[index:]) for index in range(len(x))])
  # ax[1, 1].set_xlabel('number of consecutive failures')
  # ax[1, 1].set_ylabel('P(X<=x)')
  # ax[1, 1].scatter(x, [sum(p[:index+1]) for index in range(len(x))])
  # ax[1, 2].set_xlabel('number of consecutive failures')
  # ax[1, 2].set_ylabel('accumulated successes / accumulated failures')
  # ax[1, 2].scatter(x, [sum(y[:index+1]) / ( sum(y[:index+1]) + sum(z[:index+1]) + 0) for index in range(len(x))])

  # plt.show()
  out = []
  for k in l:
    if any([v for v in k[1:]]):
      out.append(f'{k[0]} {k[1]} {k[2]}')
      if DBG:
        print(f'{k[0]} {k[1]} {k[2]}')

  clipboard.copy('\n'.join(out))

  return l


def probability_aggregate(code_1, code_2):
  data = []

  p = {
    'actorname': 'Katebrew',
    'tpt': True,
    'time_bucket': False,
    'icd': 750,
    'offset': 13080,
    'cutoff': 3710000,
    'interval': False,
    'x': 0,
    'y': 0,
  }

  data.append(probability_at_count([code_1], **p))

  p.update(
    {
      'actorname': 'Credgertwo',
      'offset': 142,
      'interval': True,
    }
  )

  # pao segment 1
  p.update(
    {
      'x': 0,
      'y': 842183,
      'st': 142,
    }
  )

  data.append(probability_at_count([code_2], **p))

  # pao segment 2
  p.update(
    {
      'x': 1094270,
      'y': 2309500,
      'st': 1090727,
    }
  )

  data.append(probability_at_count([code_2], **p))

  # pao segment 3
  p.update(
    {
      'x': 2309500,
      'y': 100000000000000000,
      'st': 2807467,
    }
  )

  data.append(probability_at_count([code_2], **p))

  # print(data)
  zipped = zip(*[v for v in data])
  out = [
    (
      z[0][0],
      z[0][1] + z[1][1] + z[1][1],
      z[0][2] + z[1][2] + z[1][2],
    )
    for z in zipped
  ]
  x = [v[0] for v in out if (v[1] or v[2])]

  y = [v[1] for v in out if (v[1] or v[2])]
  s = [sum(y[:k]) / sum(y) for k in range(len(x))]
  # for k in out:
  #   if ( any([v for v in k[1:]])):
  #     print(f"{k[0]} {k[1]} {k[2]}")
  # for k in range(len(x)):
  #   print(s[k])
