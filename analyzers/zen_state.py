from dataclasses import dataclass, field
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
          _id = player.get('id')
          # name = player.get('name')
          self.event_data['monk_id'] = _id
          return {}
          # return {'filterExpression': f"target.name = '{name}' or source.name = '{name}'"}

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
  keys = list(reports.keys())[: 4]
  report_dict = {k: v for k, v in reports.items() if k in keys}

  values = []

  if not MP:
    values = analyzer(report_dict)

  if MP:
    values = multiprocess_cb(analyzer, report_dict)

  return values

@dataclass
class Event:
  timestamp: int
  amount: int
  abilityGameID: int
  source: int
  target: int
  instance: int

  @staticmethod
  def new(event, keys):
    # keys |= set(event.keys())
    return Event(event.get('timestamp'),
                event.get('amount') + event.get('absorbed', 0) + event.get('overkill', 0),
                event.get('extraAbilityGameID') if event.get('type') == 'absorbed' else event.get('abilityGameID'),
                event.get('sourceID'),
                event.get('attackerID') if event.get('type') == 'absorbed' else event.get('targetID'),
                event.get('attackerInstance') if event.get('type') == 'absorbed' else event.get('sourceInstance'),
                )

keys = set()
ct = 0
@dataclass(init=False)
class StaggerEvent:
  absorb: Event
  damage: Event
  current_hp: int
  max_hp: int

  def validate(self, s):
    # print(self, self.damage.timestamp - self.absorb.timestamp)
    conds = (self.absorb.source == self.damage.target or self.damage.target == -1,
             self.absorb.target == self.damage.source or self.absorb.target == -1,
             self.absorb.instance == self.damage.instance or self.absorb.target == -1,
             self.absorb.abilityGameID == self.damage.abilityGameID,
             abs(self.absorb.timestamp - self.damage.timestamp) < 27,
             self.max_hp is not None
             )
    print(fmt_timestamp(self.absorb.timestamp - s.params.get('startTime')))
    print(self, '\n  ', end='')
    for c in conds:
      print(c, end=' ')
    print()
    # global ct
    # if ct > 1:
    #   raise SystemExit
    # ct += 1
    assert all(conds)

def vis():
  def combatantinfo(self, event):
    if event.get('sourceID') != self.event_data['monk_id']:
      return
    if event.get('timestamp') > self.params.get('startTime') + 30:
      return
    talents = event.get('talentTree', {})
    for talent in talents:
      if talent.get('id') == 124851:
        self.event_data['has_zen_state'] = True
        break

  def absorb(self, event):
    print('  ', event)
    e = StaggerEvent()
    e.absorb = Event.new(event, keys)
    e.current_hp = self.event_data['current_hp']
    e.max_hp = self.event_data['max_hp']
    self.event_data['events'].append(e)

  def damage_taken(self, event):
    if event.get('abilityGameID') == 124255:
      return
    if event.get('targetID') != self.event_data['monk_id']:
      return
    if not len(self.event_data['events']):
      return
    e = self.event_data['events'][-1]
    if hasattr(e, 'damage'):
      return
    print('  ', event)
    e.damage = Event.new(event, keys)
    e.validate(self)

  def max_hp(self, event):
    if event.get('type') == 'combatantinfo':
      return
    if event.get('targetID') != self.event_data['monk_id']:
      return
    self.event_data['current_hp'] = event.get('hitPoints')
    self.event_data['max_hp'] = event.get('maxHitPoints')

  def _vis(report_dict, pipe=None):
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
          'type': 'damage',
          'hitType': 1,
          'callback': damage_taken
        },
        {
          'type': 'heal',
          'callback': max_hp
        }
      ],
      event_data={'has_zen_state': False, 'current_hp': 0, 'max_hp': 0, 'events': []},
    )

    return rv.event_data

  out = process_analyzer(_vis, MP=False)
  x = [
    event.current_hp / event.max_hp
    for event in out['events']
  ]
  y = [
    event.absorb.amount / event.damage.amount
    for event in out['events']
  ]
  z = out['events']
  import matplotlib.pyplot as plt
  plt.style.use('dark_background')
  fig = plt.figure()
  ax1 = fig.add_subplot()
  ax1.scatter(x, y, picker=True)
  def onpick(event):
    ind = event.ind
    print(ind, z[ind[0]])
  fig.canvas.mpl_connect('pick_event', onpick)
  plt.show()
