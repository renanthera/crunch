from .helper import *
from copy import deepcopy

bok = 205523
fob = 457271


def fmt_timestamp(timestamp):
  timestamp_s = timestamp // 1000
  timestamp_m = timestamp_s // 60
  timestamp_h = timestamp_m // 60
  return f'{timestamp_h % 60:02}:{timestamp_m % 60:02}:{timestamp_s % 60:02}.{timestamp % 1000:03}'


def cb(self, event):
  if event.get('sourceID') not in self.event_data['info'].keys():
    self.event_data['info'][event.get('sourceID')] = deepcopy(
      self.event_data['info_base']
    )

  info = self.event_data['info'][event.get('sourceID')]

  if event.get('abilityGameID') == fob:
    info['has_applied'] = True

  if event.get('abilityGameID') == bok:
    if (
      info['previous'] is not None
      and info.get('previous', {}).get('abilityGameID') == fob
    ):
      info['data'][info['count_since_last']]['successful'] += 1
      info['count_since_last'] = 0
    else:
      info['data'][info['count_since_last']]['failed'] += 1
      info['count_since_last'] += 1

  if False:
    print(fmt_timestamp(event.get('timestamp') - self.params['startTime']), end=' ')
    print(event.get('sourceID'), end='\t')
    if event.get('abilityGameID') == bok:
      print('BOK', info['count_since_last'])
    if event.get('abilityGameID') == fob:
      print('FOB')

  info['previous'] = event


def counts(report_codes):
  clause_1 = f"type = 'applybuff' and ability.id = {fob}"
  clause_2 = f"type = 'cast' and ability.id = {bok}"
  t = Analyzer(
    report_codes,
    params={'limit': 25000, 'filterExpression': f'({clause_1}) or ({clause_2})'},
    callbacks=[{'any': True, 'callback': cb}],
    event_data={
      'info_base': {
        'data': [{'index': k, 'failed': 0, 'successful': 0} for k in range(0, 30)],
        'count_since_last': 0,
        'has_applied': False,
        'previous': None,
      },
      'info': {},
    },
  )

  o = {}
  for fight in t.data:
    for data in fight['event_data']['info'].values():
      if not isinstance(data, int) and any(
        [index['successful'] for index in data['data']]
      ):
        for index in data['data']:
          o.setdefault(index['index'], {'SUCCESS': 0, 'FAIL': 0})
          o[index['index']]['SUCCESS'] += index['successful']
          o[index['index']]['FAIL'] += index['failed']

  l = [(key, value['SUCCESS'], value['FAIL']) for key, value in o.items()]
  print('raw data (consecutive failure count, successes at x, fails at x)')
  print(l)

  import matplotlib.pyplot as plt

  x = [v[0] for v in l if (v[1] or v[2])]

  y = [v[1] for v in l if (v[1] or v[2])]

  z = [v[2] for v in l if (v[1] or v[2])]

  p = [y[i] / (y[i] + z[i]) for i in range(len(z))]

  print('successes', sum(y))
  print('fails', sum(z))
  print('attempts', sum(y) + sum(z))

  plt.style.use('dark_background')
  _, ax = plt.subplots(2, 3)
  ax[0, 0].set_xlabel('number of consecutive failures')
  ax[0, 0].set_ylabel('success')
  ax[0, 0].scatter(x, y)
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
      sum(y[: index + 1]) / (sum(y[: index + 1]) + sum(z[: index + 1]))
      for index in range(len(x))
    ],
  )

  plt.show()
