import wcl

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
          return {'sourceID': player.get('id')}

  return _fight_params_update


def gen_report_dict():
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
  return {
    k: v
    for k, v in wcl.getReportCodesFromRanks(params).items()
    if k[:2] != 'a:'
    if k != 'gk6JjQd4pXctCzvM'
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
  # keys = list(reports.keys())[: 2**10]
  keys = list(reports.keys())[: 2**6]
  # keys = list(reports.keys())[:1]
  report_dict = {k: v for k, v in reports.items() if k in keys}

  values = []

  if not MP:
    values = analyzer(report_dict)

  if MP:
    values = multiprocess_cb(analyzer, report_dict)

  return values


def trailing_window_size():
  def window_analyzer(report_dict, pipe=None):
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

    def pe_apply(self, event):
      self.event_data['previous_pe'] = event.get('timestamp')

    def validate_fight(self, event):
      items = [237673, 237671, 237676, 237672, 237674]
      self.skip_to_next_fight = [
        item.get('id', -1) in items for item in event.get('gear', [])
      ].count(True) < 4

    rv = Analyzer(
      report_dict.keys(),
      per_fight_analysis=False,
      fight_filter=gen_fight_filter(report_dict),
      fight_params_update=gen_fight_params_update(report_dict),
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

  values = process_analyzer(window_analyzer, MP=True)
  # import matplotlib.pyplot as plt

  # plt.style.use('dark_background')
  # plt.hist([e.get('delta') for e in values], log=True, bins=50)
  # plt.show()

  values.sort(key=lambda e: e.get('delta', -1), reverse=True)
  print(len(values))
  for e in values[:25]:
    print(fmt_timestamp(e.get('cb_timestamp')), end=' ')
    print(e)


def match_trigger_windows():
  class SlidingWindow:
    preceeding_window_size = 100
    trailing_window_size = 60

    def reset(self):
      self.left_index = 0
      self.center_index = 0
      self.right_index = 0
      self.events_in_window = []

    def __init__(self):
      self.reset()

    def set_event_stream(self, event_stream):
      self.reset()
      self.event_stream = event_stream
      self.event_stream_size = len(event_stream)

    def timestamp_at_index(self, index):
      return self.event_stream[index].get('timestamp')

    def convert_events_to_fingerprint(self):
      return {
        type: {
          id: len(
            [
              event
              for event in self.events_in_window
              if event.get('type') == type and event.get('abilityGameID') == id
            ]
          )
          for event in self.events_in_window
          if event.get('type') == type
          if (id := event.get('abilityGameID')) is not None
        }
        for type in {
          event.get('type')
          for event in self.events_in_window
          if event.get('type') is not None
        }
      }

    def convert_events_to_fingerprint_2(self):
      return {
        type: {
          event.get('abilityGameID')
          for event in self.events_in_window
          if event.get('type') == type
          if event.get('abilityGameID') is not None
        }
        for type in {
          event.get('type')
          for event in self.events_in_window
          if event.get('type') is not None
        }
      }

    def convert_events_to_fingerprint_3(self):
      return {
        f'{type}-{id}'
        for event in self.events_in_window
        if (type := event.get('type')) is not None
        if (id := event.get('abilityGameID')) is not None
      }

    def update_window(self, center_index):
      self.center_index = center_index

      while (
        self.timestamp_at_index(self.right_index)
        < self.timestamp_at_index(self.center_index) + self.trailing_window_size
      ):
        if self.right_index + 1 >= self.event_stream_size:
          break
        self.right_index += 1
        self.events_in_window.append(self.event_stream[self.right_index])

      while (
        self.timestamp_at_index(self.left_index)
        < self.timestamp_at_index(self.center_index) - self.preceeding_window_size
      ):
        self.left_index += 1
        self.events_in_window.pop(0)

      return self.convert_events_to_fingerprint_3()

  def trigger_window_analyzer(report_dict, pipe=None):
    sw = SlidingWindow()

    def callback(self, event):
      # this is wrong, as it doesn't include only the trailing window interval
      # and would skip if CB/CI occurs in the preceeding window interval
      window = sw.update_window(self.event_id)
      if "cast-322507" in window or "cast-1241059" in window:
        return
      self.event_data['window_fingerprints'].append(window)

    rv = Analyzer(
      report_dict.keys(),
      per_fight_analysis=False,
      fight_filter=gen_fight_filter(report_dict),
      fight_params_update=gen_fight_params_update(report_dict),
      params={'limit': 25000},
      callbacks=[
        {
          'abilityGameID': 1239483,
          'callback': callback
        }
      ],
      event_data={'window_fingerprints': []},
      preprocess=lambda s: sw.set_event_stream(s.events),
      postprocess=lambda _: sw.reset(),
    )

    if pipe is not None:
      pipe.send(rv.event_data.get('window_fingerprints', []))
    else:
      return rv.event_data.get('window_fingerprints', [])

  values = process_analyzer(trigger_window_analyzer, MP=False)

  found = []
  dedup = []
  for value in values:
    if value in found:
      index = found.index(value)
      dedup[index] += 1
    else:
      found.append(value)
      dedup.append(1)

  print(f"""number required fingerprint matches, number of observed fingerprints
  preceeding window size {SlidingWindow.preceeding_window_size}
  trailing window size {SlidingWindow.trailing_window_size}""")
  for k in range(max(dedup) + 1):
    print(k, len([v for v in dedup if v >= k]))
