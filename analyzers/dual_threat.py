from .helper import *
from copy import deepcopy
import wcl

triggers = [
  100780,  # tp
  451250,  # shadow
  450620,  # left flurry
  450617,  # right flurry
  205523,  # bok
  185099,  # rsk
  121253,  # ks
  148187,  # rjw
  # 1,      # melee
  115181,  # bof
  # 123723, # bof dot
  322109,  # tod
  132467,  # cw
  325153,  # ek
  # 388867, # ek secondary
  115129,  # eh
]

success = [
  1242373,  # stomp
]


# actorname = 'Katebrew'
# tpt = True
# time_bucket = False
# icd = 750
# offset = 13080
# cutoff = 3710000
# interval = False
# x = 0
# y = 0

# actorname = 'Credgertwo'
# offset = 142
# interval = True

# # pao segment 1
# x = 0
# y = 842183
# st = 142

# # pao segment 2
# x = 1094270
# y = 2309500
# st = 1090727

# # pao segment 3
# x = 2309500
# y = 100000000000000000
# st = 2807467


def fight_params_update(self):
  def entry_match_fn(id):
    return lambda combatant_info: any(
      [
        talent.get('id') == id
        for talent in [
          entry
          for tree in ['talentTree', 'talent_tree']
          for entry in combatant_info.get(tree, [])
        ]
      ]
    )

  players = [
    f"'{player}'"
    for player in wcl.getPlayerNameWith(self.params, entry_match_fn(125020))
  ]
  player_names = ', '.join(players)
  clause_0 = f'(source.name in ({player_names}))'

  clause_2_ids = [1, 451839]
  clause_2 = f'(ability.id in ({", ".join((str(x) for x in clause_2_ids))}))'

  clauses = ' or '.join([clause_2])
  return {'filterExpression': f'{clause_0} and ({clauses})'}


def fmt_timestamp(timestamp):
  timestamp_s = timestamp // 1000
  timestamp_m = timestamp_s // 60
  timestamp_h = timestamp_m // 60
  return f'{timestamp_h % 60:02}:{timestamp_m % 60:02}:{timestamp_s % 60:02}.{timestamp % 1000:03}'


def cb(self, event):
  params = self.event_data.get('blob')
  actorname = params.get('actorname')
  tpt = params.get('tpt')
  time_bucket = params.get('time_bucket')
  icd = params.get('icd')
  offset = params.get('offset')
  cutoff = params.get('cutoff')
  interval = params.get('interval')
  x = params.get('x')
  y = params.get('y')
  st = params.get('st')
  timestamp = event.get('timestamp') - offset
  # print(fmt_timestamp(timestamp), timestamp)
  # print(self.params)
  # raise SystemExit

  # select interval for badly constrained logs
  # if timestamp > cutoff and tpt: # cutoff
  #   return
  # if timestamp < cutoff and not tpt: # cutoff
  #   return

  if interval and (
    (not (timestamp > x and timestamp < y)) or self.params.get('startTime') != st
  ):
    return

  # duplicate info_base per filtered actor
  if event.get('sourceID') not in self.event_data['info'].keys():
    self.event_data['info'][event.get('sourceID')] = deepcopy(
      self.event_data['info_base']
    )

  # filter misses
  if event.get('hitType') == 0:
    return

  # nice friendly ref
  info = self.event_data['info'][event.get('sourceID')]

  # filter for icd
  if icd and event.get('abilityGameID') in triggers:
    if (
      info['last_trigger_attempt'] != 0
      and info['last_trigger_attempt'] > event.get('timestamp') - icd
    ):
      return

  if icd and event.get('abilityGameID') in success:
    if (
      info['last_success'] != 0 and info['last_success'] > event.get('timestamp') - icd
    ):
      return

  # if event bucketing, increment index
  if event.get('abilityGameID') in triggers and not time_bucket:
    info['count_since_last'] += 1

  # calculate index for time bucketing and event bucketing
  index = 0
  if time_bucket:
    index = (event.get('timestamp') - info['count_since_last']) // 1000
  else:
    index = info['count_since_last']

  # print(time_bucket,index)
  if event.get('abilityGameID') in success:
    # print('SUCCESS',fmt_timestamp(timestamp), f"({fmt_timestamp(event.get('timestamp')-info['last_success'])})", event.get('timestamp')-info['last_success']>=icd)
    was_zero = info['count_since_last'] == 0
    if time_bucket:
      info['count_since_last'] = event.get('timestamp')
    else:
      info['count_since_last'] = 0

    if was_zero:
      return

    info['last_success'] = event.get('timestamp')
    info['data'][index]['successful'] += 1

  if info['count_since_last'] == 0:
    return

  if event.get('abilityGameID') in triggers:
    # print('ATTEMPT',fmt_timestamp(timestamp),f"({fmt_timestamp(event.get('timestamp')-info['last_trigger_attempt'])})", event.get('timestamp')-info['last_trigger_attempt']>=icd)
    info['data'][index]['failed'] += 1
    info['last_trigger_attempt'] = event.get('timestamp')

  # if False:
  #   print( fmt_timestamp( event.get('timestamp') - self.params['startTime'] ), end=' ' )
  #   print( event.get( 'sourceID' ), end='\t')
  #   if event.get( 'abilityGameID' ) == 1:
  #     print( "MELEE", info[ 'count_since_last' ], event.get( 'hitType' ) )
  #   if event.get( 'abilityGameID' ) == 451839:
  #     print( "DUAL THREAT" )


def probability_at_count(report_codes, **params):
  actorname = params.get('actorname')
  tpt = params.get('tpt')
  time_bucket = params.get('time_bucket')
  icd = params.get('icd')
  offset = params.get('offset')
  cutoff = params.get('cutoff')
  interval = params.get('interval')
  x = params.get('x')
  y = params.get('y')
  st = params.get('st')
  t = Analyzer(
    report_codes,
    params={
      'limit': 25000,
      'filterExpression': f"ability.id in ({', '.join([str(v) for v in [*triggers, *success]])}) and source.name = '{actorname}'",
      # 'filterExpression': "ability.id in (1, 451839) and source.name = 'Pepeg'"
      # 'filterExpression': "type='combatantinfo'"
    },
    callbacks=[
      {
        'type': 'damage',
        # 'abilityGameID': [ 1, 451839 ],
        'abilityGameID': [*triggers, *success],
        'callback': cb,
      }
    ],
    event_data={
      'blob': params,
      'info_base': {
        'data': [{'index': k, 'failed': 0, 'successful': 0} for k in range(0, 1000)],
        'count_since_last': 0,
        'last_trigger_attempt': 0,
        'last_success': 0,
      },
      'info': {},
    },
    # fight_params_update=fight_params_update
  )

  o = {}
  for fight in t.data:
    for _, data in fight['event_data']['info'].items():
      for index in data['data']:
        o.setdefault(index['index'], {'SUCCESS': 0, 'FAIL': 0})
        o[index['index']]['SUCCESS'] += index['successful']
        o[index['index']]['FAIL'] += index['failed']
        # if index[ 'index' ] > 14 and ( index[ 'failed' ] + index[ 'successful' ] > 0 ):
        # print( fight[ 'report_code' ], fight[ 'fight_id' ] )
        # print( player )
        # print( index )

  l = [(key, value['SUCCESS'], value['FAIL']) for key, value in o.items()]

  x = [v[0] for v in l if (v[1] or v[2])]

  y = [v[1] for v in l if (v[1] or v[2])]

  z = [v[2] for v in l if (v[1] or v[2])]

  p = [y[i] / (y[i] + z[i]) for i in range(len(z))]

  # print('successes', sum(y))
  # print('fails', sum(z))
  # print('attempts', sum(y) + sum(z))
  # x = range(0,200)
  # y = [0.1 + 0.01 * k for k in x]

  import matplotlib.pyplot as plt

  plt.style.use('dark_background')
  _, ax = plt.subplots(2, 3)
  ax[0, 0].set_xlabel('number of consecutive failures')
  ax[0, 0].set_ylabel('success')
  # ax[0, 0].scatter(x, y)
  # ax[0, 0].scatter(x, [sum(y[:k]) for k in range(len(x))])
  ax[0, 0].scatter(x, [sum(y[:k]) / sum(y) for k in range(len(x))])
  r = x
  s = [sum(y[:k]) / sum(y) for k in range(len(x))]
  # for k in range(len(r)):
  #   print(s[k])
  #   # print(f'{r[k]}\t{s[k]}')
  ax[0, 1].set_xlabel('number of consecutive failures')
  ax[0, 1].set_ylabel('fail')
  ax[0, 1].scatter(x, z)
  ax[0, 2].set_xlabel('number of consecutive failures')
  ax[0, 2].set_ylabel('P(X=x)')
  ax[0, 2].scatter(x, p)
  ax[1, 0].set_xlabel('number of consecutive failures')
  ax[1, 0].set_ylabel('P(X>=x)')
  ax[1, 0].scatter(x, [sum(p[index:]) for index in range(len(x))])
  ax[1, 1].set_xlabel('number of consecutive failures')
  ax[1, 1].set_ylabel('P(X<=x)')
  ax[1, 1].scatter(x, [sum(p[: index + 1]) for index in range(len(x))])
  ax[1, 2].set_xlabel('number of consecutive failures')
  ax[1, 2].set_ylabel('accumulated successes / accumulated failures')
  ax[1, 2].scatter(
    x,
    [
      sum(y[: index + 1]) / (sum(y[: index + 1]) + sum(z[: index + 1]) + 0)
      for index in range(len(x))
    ],
  )

  plt.show()
  for k in l:
    if any([v for v in k[1:]]):
      print(f'{k[0]} {k[1]} {k[2]}')

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
