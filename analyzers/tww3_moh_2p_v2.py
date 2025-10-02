from collections import defaultdict
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
  # keys = list(reports.keys())
  # keys = list(reports.keys())[: 2**6]
  keys = list(reports.keys())[: 4]
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


def matches_expected_distribution():
  def actor_id(analyzer, aid):
    return f"{analyzer.report_code}-{analyzer.fight_id}-{aid}"

  class Child:
    def __init__(self, parent):
      self.parent = parent

    def callback_layout(self):
      return self.base_callback_layout | {'callback': self.callback()}

    def callback(self):
      assert(False)

  class TriggerAttempt(Child):
    base_callback_layout = {
      'type': [
        'damage',
        'heal'
      ],
      'abilityGameID': [
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
        # 455179,  # elixir of determination
        451253,  # mantra of purity
      ]
    }

    ICD = 5

    class Trigger:
      open = True
      icd = defaultdict(lambda: -1)
      count = 0

      def __repr__(self):
        return f"Trigger({self.open}, {self.count})"

    def callback(self):
      def __internal(analyzer, event):
        if event.get('sourceID') in self.parent.skip_list:
          return

        sid = event.get('sourceID')
        assert(sid != 0)
        aid = actor_id(analyzer, sid)
        if not len(self.parent.trigger_list[aid]):
          # print('made trigger')
          self.parent.trigger_list[aid].append(TriggerAttempt.Trigger())
        if not self.parent.trigger_list[aid][-1].open:
          # print('made trigger')
          self.parent.trigger_list[aid].append(TriggerAttempt.Trigger())

        trigger = self.parent.trigger_list[aid][-1]
        # print(aid, trigger)
        agid = event.get('abilityGameID')
        timestamp = event.get('timestamp')
        if timestamp - trigger.icd[agid] > self.ICD:
          trigger.count += 1
          trigger.icd[agid] = timestamp

      return __internal

  class PotentialEnergy(Child):
    base_callback_layout = {
      'type': [
        'applybuff',
        'applybuffstack',
        'removebuffstack',
        'removebuff',
        'refreshbuff'
      ],
      'abilityGameID': 1239483
    }

    MAX_DELTA = 60
    FORCE_SOURCES = [
      322507,
      1241059
    ]

    def callback(self):
      def __internal(analyzer, event):
        tid = event.get('sourceID')
        if tid in self.parent.skip_list:
          return
        event_timestamp = event.get('timestamp')
        next_force = -1
        # print('start search at', event_timestamp)
        for peek in analyzer.events[analyzer.event_id+1:]:
          peekstamp = peek.get('timestamp')
          if peekstamp - event_timestamp > self.MAX_DELTA:
            # print('  canceled search at', peekstamp, f"({peekstamp - event_timestamp})")
            break
          if peek.get('abilityGameID') == self.base_callback_layout['abilityGameID']:
            if peek.get('type') in ['applybuff', 'applybuffstack', 'refreshbuff']:
              # print('another trigger before possible force', peek)
              break
          if peek.get('abilityGameID') in self.FORCE_SOURCES:
            if peek.get('type') == 'cast':
              # print('  found at', peekstamp, f"({peekstamp - event_timestamp})")
              next_force = peekstamp
              break

        assert(next_force is not None)
        aid = actor_id(analyzer, tid)
        st = analyzer.params.get('startTime')
        # no force found, must be natural
        # TODO: handle end of fight?
        event_type = event.get('type')
        assert event_type is not None
        # print(fmt_timestamp(event_timestamp - st), self.parent.pe_count, event)
        if event_type == 'removebuffstack':
          self.parent.pe_count = event.get('stack')
        if event_type == 'removebuff':
          # TODO: handle expiry maybe and then this can be readded
          # assert self.parent.pe_count == 1
          self.parent.pe_count = 0

        if event_type in ['applybuff', 'applybuffstack'] or (event_type == 'refreshbuff' and self.parent.pe_count == 6):
          if next_force == -1:
            self.parent.pe_count = min(self.parent.pe_count + 1, 6)
            # print('natural')
            # print(fmt_timestamp(event_timestamp - st))
            # print(event)
            # print(self.parent.trigger_list[aid][-1])
            if not self.parent.trigger_list[aid][-1].open:
              copy = self.parent.trigger_list[aid][-1]
              self.parent.trigger_list[aid].append(copy)
            self.parent.trigger_list[aid][-1].open = False

          # force found, cannot be natural
          elif next_force > -1:
            self.parent.pe_count = min(self.parent.pe_count + 2, 6)
            # print('force')
            # print(fmt_timestamp(event_timestamp - st), fmt_timestamp(next_force - st))
            # print(event)
            # print(self.parent.trigger_list[aid][-1])
            if len(self.parent.force_list[aid]) and self.parent.force_list[aid][-1].open:
              self.parent.force_list[aid].append(self.parent.trigger_list[aid].pop())
              self.parent.force_list[aid][-1].open = False

      return __internal

  def post_process(analyzer):
    dt = analyzer.event_data['distribution_tracker']
    for aid, tl in dt.trigger_list.items():
      if len(tl):
        if tl[-1].open:
          tl.pop()
        analyzer.event_data['trigger_list'][aid] += tl
    # for aid, fl in dt.force_list.items():
    #   if len(fl):
    #     print('good fl', aid)
    #     analyzer.event_data['force_list'][aid] += fl
    #   else:
    #     print('bad fl', aid)
    dt.skip_map = []
    dt.trigger_list = defaultdict(list)
    dt.force_list = defaultdict(list)
    dt.pe_stacks = 0
    for tl in dt.trigger_list.values():
      # assert len(tl)
      if len(tl) and tl[-1].open:
        tl.pop()

  class Death(Child):
    base_callback_layout = {
      'type': 'death'
    }

    def callback(self):
      def __internal(analyzer, event):
        self.parent.skip_list.append(event.get('targetID'))
        assert len(self.trigger_list[actor_id(analyzer, event)])
        if self.parent.trigger_list[actor_id(analyzer, event)][-1].open:
          self.parent.trigger_list[actor_id(analyzer, event)].pop()

  class DistributionTracker:
    children = [PotentialEnergy, TriggerAttempt]

    def __init__(self):
      self.child_classes = [c(self) for c in self.children]
      self.callbacks = [c.callback_layout() for c in self.child_classes]

      self.skip_list = []
      self.pe_count = 0
      self.trigger_list = defaultdict(list)
      self.force_list = defaultdict(list)

  def distribution_analyzer(report_dict, pipe=None):
    dt = DistributionTracker()
    rv = Analyzer(
      report_dict,
      per_fight_analysis=False,
      fight_filter=gen_fight_filter(report_dict),
      fight_params_update=gen_fight_params_update(report_dict),
      params={'limit': 25000},
      event_data={
        'distribution_tracker': dt,
        'trigger_list': defaultdict(list),
        'force_list': defaultdict(list)
        },
      callbacks=dt.callbacks,
      postprocess=post_process
    )

    if pipe is not None:
      pipe.send(rv.event_data.get('trigger_list', []))
    else:
      return rv.event_data.get('trigger_list', [])

  values = process_analyzer(distribution_analyzer, MP=False)
  # values.sort(key=lambda v: v.count)
  # print(values.keys())
  # print(sum(1 for v in values if v.open))
  import matplotlib.pyplot as plt
  from mplcursors import cursor
  plt.style.use('dark_background')
  fig, ax = plt.subplots()
  m = max(v.count for e in values.values() for v in e)
  print(m)
  lines = [
      ax.plot(range(1,m), [
        sum(1 for v in vals if v.count <= i) / count for i in range(1, m)],
               label=aid)[0]
      for aid, vals in values.items()
      if (count := len(vals))
  ]
  leg = ax.legend()
  map = {}
  for legend_line, ax_line in zip(leg.get_lines(), lines):
    legend_line.set_picker(6)
    map[legend_line] = ax_line

  def on_pick(e):
    legend_line = e.artist
    if legend_line not in map:
      return
    al = map[legend_line]
    print(al)
    visible = not al.get_visible()
    al.set_visible(visible)
    legend_line.set_alpha(1.0 if visible else 0.2)
    fig.canvas.draw()

  fig.canvas.mpl_connect('pick_event', on_pick)
  c = cursor(hover=True)
  @c.connect("add")
  def _(sel):
    print(sel.artist)

  plt.show()
