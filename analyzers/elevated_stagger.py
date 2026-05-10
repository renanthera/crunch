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
          self.event_data['monk_id'] = player.get('id')
          return {'targetID': player.get('id')}

  return _fight_params_update


def gen_report_dict():
  params = {
    'id': 47,
    'leaderboard': 'LogsOnly',
    'className': 'Monk',
    'specName': 'Brewmaster',
    'pagination_limit': 1,
  }

  return {
    k: v
    for k, v in wcl.getReportCodesFromRanksZone(params).items()
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
  # keys = reports.keys()
  keys = list(reports.keys())[: 1]
  report_dict = {k: v for k, v in reports.items() if k in keys}

  values = []

  if not MP:
    values = analyzer(report_dict)

  if MP:
    values = multiprocess_cb(analyzer, report_dict)

  return values


def timing():
  def window_analyzer(report_dict, pipe=None):
    def elevate_occurred(self, event):
      if not self.event_data['satisfied'] and (self.event_data['timestamp'] - event.get('timestamp')) ** 2 <= 1:
        self.event_data['unsatisfied_count'] += 1
        self.event_data['events'].append(event.get('timestamp'))
        print('  !', fmt_timestamp(event.get('timestamp') - self.params.get('startTime')), event.get('timestamp'))
      else:
        print('  =', fmt_timestamp(event.get('timestamp') - self.params.get('startTime')), event.get('timestamp'))

      self.event_data['timestamp'] = event.get('timestamp')
      self.event_data['satisfied'] = False

    def absorb_occurred(self, event):
      if not self.event_data['satisfied'] and (self.event_data['timestamp'] - event.get('timestamp')) ** 2 <= 1:
        self.event_data['satisfied'] = True
        # self.event_data['events'].append({'stagger_pool_state': self.event_data['last_tick']} | event)
        print('  +', fmt_timestamp(event.get('timestamp') - self.params.get('startTime')), event.get('timestamp'), event.get('amount'))
      else:
        print('   ', fmt_timestamp(event.get('timestamp') - self.params.get('startTime')), event.get('timestamp'), event.get('amount'))

    def tick_occurred(self, event):
      self.event_data['last_tick'] = event.get('unmitigatedAmount')
      # if event.get('maxHitPoints') is not None:
      #   self.event_data['last_tick'] = event.get('unmitigatedAmount') / event.get('maxHitPoints')

    def reset(self):
      self.event_data['timestamp'] = -1
      self.event_data['satisfied'] = True
      self.event_data['last_tick'] = -1

    rv = Analyzer(
      report_dict.keys(),
      per_fight_analysis=True,
      fight_filter=gen_fight_filter(report_dict),
      fight_params_update=gen_fight_params_update(report_dict),
      params={
        'limit': 25000,
        'includeResources': True
      },
      callbacks=[
        {
          'type': 'absorbed',
          'abilityGameID': 115069,
          'callback': absorb_occurred,
        },
        {
          'type': 'damage',
          'abilityGameID': 124255,
          'callback': tick_occurred
        },
        {
          # 'type': ['applybuff', 'refreshbuff'],
          'type': 'refreshbuff',
          'abilityGameID': 1260619,
          'callback': elevate_occurred,
        },
      ],
      event_data={'timestamp': -1, 'satisfied': True, 'unsatisfied_count': 0, 'last_tick': -1, 'events': []},
      preprocess=reset,
      postprocess=reset
    )

    return rv.data

  values = process_analyzer(window_analyzer, MP=False)
  for entry in values:
    print(entry)

  def staggered_amounts(report_dict, pipe=None):
    def absorbed(self, event):
      entry = None
      for value in values:
        if value.get('report_code') == self.report_code and value.get('fight_id') == self.fight_id:
          entry = value.get('event_data', {}).get('events')
          break
      assert entry is not None
      if event.get('timestamp') in entry:
        self.event_data['events'].append(event)

    rv = Analyzer(
      report_dict.keys(),
      fight_filter=gen_fight_filter(report_dict),
      fight_params_update=gen_fight_params_update(report_dict),
      params={
        'limit': 25000,
        'includeResources': True
      },
      callbacks=[
        {
          'type': 'absorbed',
          'abilityGameID': 115069,
          'callback': absorbed
        }
      ],
      event_data={'events': []}
    )

    return rv.event_data

  out = process_analyzer(staggered_amounts, MP=False)
  for v in out.get('events'):
    print(v)

  q = [
    e.get('amount')
    for e in out.get('events')
  ]

  print(min(q), max(q), sum(q) / len(q))
  print(sorted(q))

def elevated_stagger_vis():
  def pp(self):
    raise SystemExit

  def combatantinfo(self, event):
    if event.get('sourceID') != self.params.get('targetID'):
      return
    if event.get('timestamp') > self.params.get('startTime') + 30:
      return
    talents = event.get('talentTree', {})
    self.event_data['ticks'] = 20
    for talent in talents:
      if talent.get('id') == 124992:
        self.event_data['ticks'] = 30
        break
    self.event_data['ticks_remaining'] = self.event_data['ticks']

  def expected_tick_size(self):
    return self.event_data['pool'] / self.event_data['ticks_remaining']

  def absorb(self, event):
    print(f'  + {fmt_timestamp(event.get('timestamp') - self.params.get('startTime'))} {event.get("amount")}')
    self.event_data['pool'] += event.get('amount')
    self.event_data['ticks_remaining'] = self.event_data['ticks']

  def touch_of_death(self, event):
    print(event)
    self.event_data['touch_of_death_amount'] = event.get('amount')

  def clear(self, event):
    # BUG: TOUCH OF DEATH REMOVES ENTIRE POOL?
    # if abs(self.event_data['touch_of_death_amount'] - event.get('amount')) <= 5:
    if self.event_data['touch_of_death_amount'] != 0:
      print(f'  - {fmt_timestamp(event.get('timestamp') - self.params.get('startTime'))} TOD {event.get("amount")}')
      self.event_data['touch_of_death_amount'] = 0
      self.event_data['pool'] = 0
      # self.event_data['pool'] -= event.get('amount')
    else:
      print(f'  - {fmt_timestamp(event.get('timestamp') - self.params.get('startTime'))} {event.get("amount")}')
      self.event_data['pool'] -= event.get('amount') * self.event_data['ticks_remaining']
    print('P: ', self.event_data['pool'])

  def tick(self, event):
    expected = expected_tick_size(self)
    tick_size = event.get('unmitigatedAmount')
    should_exit = False

    # validate
    print(f'  = {fmt_timestamp(event.get('timestamp') - self.params.get('startTime'))} {tick_size} [{tick_size * (self.event_data["ticks_remaining"] - 1)}] ({expected}, {abs(tick_size - expected)})')
    if (expected - tick_size) ** 2 > 0.05 * tick_size and self.event_data['last_tick'] != -1:
      print(fmt_timestamp(event.get('timestamp') - self.params.get('startTime')), event.get('timestamp'))
      print('  ', expected, tick_size, self.event_data)
      should_exit = True

    self.event_data['ticks_remaining'] -= 1
    self.event_data['last_tick'] = tick_size
    self.event_data['pool'] = tick_size * self.event_data['ticks_remaining']

    if should_exit:
      raise SystemExit

  def vis(report_dict, pipe=None):
    rv = Analyzer(
      report_dict.keys(),
      fight_filter=gen_fight_filter(report_dict),
      fight_params_update=gen_fight_params_update(report_dict),
      params={
        'limit': 25000,
        'includeResources': True
      },
      callbacks=[
        {
          'type': 'combatantinfo',
          'callback': combatantinfo
        },
        {
          'type': 'absorbed',
          'abilityGameID': 115069,
          'callback': absorb
        },
        {
          'type': ['staggerclear', 'staggerprevented'],
          'callback': clear
        },
        {
          'type': 'damage',
          'abilityGameID': 322109,
          'callback': touch_of_death
        },
        {
          'type': 'damage',
          'abilityGameID': 124255,
          'callback': tick
        }
      ],
      event_data={'last_tick': -1, 'pool': 0, 'ticks': 20, 'ticks_remaining': 0, 'touch_of_death_amount': 0},
      postprocess=pp
    )

    return rv.event_data

  out = process_analyzer(vis, MP=False)
  # TODO: implement vis
