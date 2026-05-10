import wcl
import math

from .helper import Analyzer

def fmt_timestamp(timestamp):
  timestamp_s = timestamp // 1000
  timestamp_m = timestamp_s // 60
  timestamp_h = timestamp_m // 60
  return f'{timestamp_h % 60:02}:{timestamp_m % 60:02}:{timestamp_s % 60:02}.{timestamp % 1000:03}'


def gen_fight_filter(codes):
  def _fight_filter(self, fight_data):
    return any(
      [
        fight_data.get('id') == fight.get('fightID', -1)
        for fight in codes[self.report_code]
      ]
    )

  return _fight_filter


def gen_fight_params_update(code_dict):
  def _fight_params_update(self):
    for player in wcl.getPlayers(self.params):
      for fight in code_dict[self.report_code]:
        if player.get('name') == fight.get('name', '') and self.fight_id == fight.get(
          'fightID'
        ):
          self.event_data['valid_source'].add(player.get('id'))
          return {}

  return _fight_params_update


def gen_report_dict():
  params = {
    'id': 3129,
    'partition': 3,
    # 'difficulty': 3,
    'className': 'Monk',
    'specName': 'Brewmaster',
    # 'filter': 'abilities.450763',
    'pagination_limit': 5,
  }

  # filter anon logs to make additional actor filtering logic unnecessary
  # filter that one log because something weird happened with its combatantinfo
  return {
    k: v
    for k, v in wcl.getReportCodesFromRanks(params).items()
    if k[:2] != 'a:'
  }


def process_analyzer(analyzer, MP):
  def multiprocess_cb(fn, report_dict):
    from multiprocessing import Pipe, Process

    thread_count = 32
    keys = list(report_dict.keys())
    block_size = len(keys) // thread_count
    jobs = []
    pipes = []
    values = []
    for thread in range(thread_count):
      recv, send = Pipe(False)
      subdict = {
        k: v
        for k, v in report_dict.items()
        if k in keys[thread * block_size : (thread + 1) * block_size]
      }
      p = Process(
        target=fn,
        args=(subdict, send),
      )
      jobs.append(p)
      pipes.append(recv)
      p.start()

    for job in jobs:
      p.join()

    for pipe in pipes:
      values += pipe.recv()

    return values

  # don't include all report codes as it makes development kinda painful
  reports = gen_report_dict()
  # keys = list(reports.keys())
  keys = list(reports.keys())[: 2**8]
  # keys = list(reports.keys())[: 2**9]
  # keys = list(reports.keys())[: 4]
  report_dict = {k: v for k, v in reports.items() if k in keys}

  values = []

  if not MP:
    values = analyzer(report_dict)

  if MP:
    values = multiprocess_cb(analyzer, report_dict)

  return values


def intensify():
  def window_analyzer(report_dict, pipe=None):
    def reset_previous(self, event):
      self.event_data['previous_tick'] = {}
      self.event_data['valid_source'] = set()
      for player in wcl.getPlayers(self.params):
        for fight in report_dict[self.report_code]:
          if player.get('name') == fight.get('name', '') and self.fight_id == fight.get(
            'fightID'
          ):
            self.event_data['valid_source'].add(player.get('id'))

    def calc(self, event):
      source_id = event.get('sourceID')
      candidate_sources = self.event_data['valid_source']
      if source_id not in candidate_sources:
        return
      previous_ticks = self.event_data['previous_tick']
      if source_id in previous_ticks.keys():
        coeff = event.get('unmitigatedAmount') / previous_ticks[source_id]
        log = math.log(coeff, 1.2)
        self.event_data['count'] += 1
        if coeff != 1.0:
          self.event_data['coeff'].append(coeff)
        print(coeff, log, math.fabs(log-round(log)))
      previous_ticks[source_id] = event.get('unmitigatedAmount')


    def validate_fight(self, event):
      for talent in (event['talentTree'] + event['talents']):
        if talent['nodeID'] == 101227:
          return True
      print(' E: skipping, no Coalescence')
      return False

    rv = Analyzer(
      report_dict.keys(),
      per_fight_analysis=False,
      fight_filter=gen_fight_filter(report_dict),
      fight_params_update=gen_fight_params_update(report_dict),
      params={'limit': 25000, 'filterExpression': 'ability.id=450763'},
      callbacks=[
        {'type': 'combatantinfo', 'callback': validate_fight},
        {'type': 'damage', 'callback': calc},
      ],
      event_data={'previous_tick': {}, 'count': 0, 'valid_source': set(), 'coeff': []},
      preprocess=lambda s: reset_previous(s, None),
      postprocess=lambda s: reset_previous(s, None),
    )

    if pipe is not None:
      pipe.send(rv.event_data.get('coeff'), [])
    else:
      return rv.event_data.get('coeff', [])

  values = process_analyzer(window_analyzer, MP=False)
  print(values)

  import matplotlib.pyplot as plt
  import numpy as np
  plt.style.use('dark_background')
  plt.hist(sorted(values)[:-15], log=True, bins=10)
  print(sorted(values))
  plt.show()

  # values.sort(key=lambda e: e.get('delta', -1), reverse=True)
  # print(len(values))
  # for e in values[:25]:
  #   print(fmt_timestamp(e.get('cb_timestamp')), end=' ')
  #   print(e)
