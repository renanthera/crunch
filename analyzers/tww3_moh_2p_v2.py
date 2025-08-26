import clipboard
import wcl

from .helper import Analyzer

talent = [125039, 124865]
items = [237673, 237671, 237676, 237672, 237674]


def fmt_timestamp(timestamp):
  timestamp_s = timestamp // 1000
  timestamp_m = timestamp_s // 60
  timestamp_h = timestamp_m // 60
  return f'{timestamp_h % 60:02}:{timestamp_m % 60:02}:{timestamp_s % 60:02}.{timestamp % 1000:03}'


def reset_pe(self, event):
  self.event_data['previous_pe'] = -1


def cb_cast(self, event):
  if self.event_data['previous_pe'] != -1:
    self.event_data['deltas'].append(
      {
        'delta': event.get('timestamp') - self.event_data['previous_pe'],
        'cb_timestamp': event.get('timestamp') - self.params.get('startTime'),
        'code': self.report_code,
        'fight_id': self.fight_id,
      }
    )
    reset_pe(self, event)
    # print(self.event_data['deltas'][-1].get('delta'))


def pe_apply(self, event):
  self.event_data['previous_pe'] = event.get('timestamp')


def validate_fight(self, event):
  items = [237673, 237671, 237676, 237672, 237674]
  self.skip_to_next_fight = [
    item.get('id', -1) in items for item in event.get('gear', [])
  ].count(True) < 4


def windows():
  params = {
    'id': 44,
    'difficulty': 4,
    'className': 'Monk',
    'specName': 'Brewmaster',
    'filter': 'abilities.1239442',
    'pagination_limit': 1,
  }

  # filter anon logs to make additional actor filtering logic unnecessary
  # filter that one log because something weird happened with its combatantinfo
  report_dict = {
    k: v
    for k, v in wcl.getReportCodesFromRanks(params).items()
    if k[:2] != 'a:'
    if k != 'gk6JjQd4pXctCzvM'
  }

  def _fight_filter(self, fight_data):
    return any(
      [
        fight_data.get('id') == fight.get('fightID', -1)
        for fight in report_dict[self.report_code]
      ]
    )

  def _fight_params_update(self):
    for player in wcl.getPlayers(self.params):
      for fight in report_dict[self.report_code]:
        if player.get('name') == fight.get('name', '') and self.fight_id == fight.get(
          'fightID'
        ):
          return {'sourceID': player.get('id')}

  # don't include all report codes as it makes development kinda painful
  MP = True
  keys = list(report_dict.keys())[:2**10]

  # MP = False
  # keys = list(report_dict.keys())[:1]

  def window_analyzer(keys, pipe=None):
    rv = Analyzer(
      keys,
      per_fight_analysis=False,
      fight_filter=_fight_filter,
      fight_params_update=_fight_params_update,
      params={'limit': 25000},
      callbacks=[
        {'type': 'combatantinfo', 'callback': validate_fight},
        {
          'type': 'cast',
          'abilityGameID': [322507, 1241059],
          'callback': cb_cast,
        },
        {
          'type': ['applybuff', 'applybuffstack', 'refreshbuff'],
          'abilityGameID': 1239483,
          'callback': pe_apply,
        },
      ],
      event_data={'previous_pe': -1, 'deltas': []},
      preprocess=lambda s: reset_pe(s, None),
      postprocess=lambda s: reset_pe(s, None),
    )

    if pipe is not None:
      pipe.send(rv.event_data.get('deltas', []))
    else:
      return rv.event_data.get('deltas', [])

  values = []

  if not MP:
    values = window_analyzer(keys)

  if MP:
    from multiprocessing import Pipe, Process

    thread_count = 32
    block_size = len(keys) // thread_count
    jobs = []
    pipes = []
    for thread in range(thread_count):
      recv, send = Pipe(False)
      p = Process(
        target=window_analyzer,
        args=(keys[thread * block_size : (thread + 1) * block_size], send),
      )
      jobs.append(p)
      pipes.append(recv)
      p.start()

    for job in jobs:
      p.join()

    for pipe in pipes:
      values += pipe.recv()

  # import matplotlib.pyplot as plt

  # plt.style.use('dark_background')
  # plt.hist([e.get('delta') for e in values], log=True, bins=50)
  # plt.show()

  values.sort(key=lambda e: e.get('delta', -1), reverse=True)
  print(len(values))
  for e in values[:25]:
    print(fmt_timestamp(e.get('cb_timestamp')), end=' ')
    print(e)

  # # clipboard.copy('\n'.join(out))

  # return l
