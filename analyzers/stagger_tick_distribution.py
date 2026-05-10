import wcl
from .helper import Analyzer

table = [
  # {'name': 'Loomithar', 'id': 3131, 'difficulty': 2, 'type': 'raid'},
  # {'name': 'Soulbinder Naazindhri', 'id': 3130, 'difficulty': 2, 'type': 'raid'},
  # {'name': 'Soul Hunters', 'id': 3122, 'difficulty': 2, 'type': 'raid'},
  # {'name': 'Fractillus', 'id': 3133, 'difficulty': 2, 'type': 'raid'},
  # {'name': 'Dimensius', 'id': 3135, 'difficulty': 2, 'type': 'raid'},
  # 'Priory of the Sacred Flame': {'id': 62649, 'bracket': 11},
  # 'Soleahs Gambit': {'id': 112442, 'bracket': 11},
  # 'Streets of Wonder': {'id': 112441, 'bracket': 11},
  # 'Dawnbreaker': {'id': 62662 'bracket': 11},
  {'name': 'Plexus Sentinel', 'id': 44, 'difficulty': 3, 'type': 'raid'},
  {'name': 'Plexus Sentinel', 'id': 44, 'difficulty': 4, 'type': 'raid'},
  {'name': 'Plexus Sentinel', 'id': 44, 'type': 'raid'},
  {'name': 'Forgeweaver Araz', 'id': 44, 'difficulty': 3, 'type': 'raid'},
  {'name': 'Forgeweaver Araz', 'id': 44, 'difficulty': 4, 'type': 'raid'},
  {'name': 'Forgeweaver Araz', 'id': 44, 'type': 'raid'},
  {'name': 'Nexus-King Salhadaar', 'id': 44, 'difficulty': 3, 'type': 'raid'},
  {'name': 'Nexus-King Salhadaar', 'id': 44, 'difficulty': 4, 'type': 'raid'},
  {'name': 'Nexus-King Salhadaar', 'id': 44, 'type': 'raid'},
  {'name': 'Ara-Kara', 'id': 62660, 'bracket': 6, 'type': 'm+'},
  {'name': 'Ara-Kara', 'id': 62660, 'bracket': 11, 'type': 'm+'},
  {'name': 'Ara-Kara', 'id': 62660, 'type': 'm+'},
  {'name': 'Eco-Dome Aldani', 'id': 12830, 'bracket': 6, 'type': 'm+'},
  {'name': 'Eco-Dome Aldani', 'id': 12830, 'bracket': 11, 'type': 'm+'},
  {'name': 'Eco-Dome Aldani', 'id': 12830, 'type': 'm+'},
  {'name': 'Halls of Atonement', 'id': 62287, 'bracket': 6, 'type': 'm+'},
  {'name': 'Halls of Atonement', 'id': 62287, 'bracket': 11, 'type': 'm+'},
  {'name': 'Halls of Atonement', 'id': 62287, 'type': 'm+'},
  {'name': 'Floodgate', 'id': 62773, 'bracket': 6, 'type': 'm+'},
  {'name': 'Floodgate', 'id': 62773, 'bracket': 11, 'type': 'm+'},
  {'name': 'Floodgate', 'id': 62773, 'type': 'm+'},
]

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


def gen_report_dict(mode):
  params = {
    'id': mode.get('id'),
    'metric': 'dps',
    'leaderboard': 'LogsOnly',
    'className': 'Monk',
    'specName': 'Brewmaster',
    # 'difficulty': 4,
    'pagination_limit': 10,
    # 'pagination_limit': 5,
  }

  if 'bracket' in mode.keys():
    params['bracket'] = mode.get('bracket')
  if 'difficulty' in mode.keys():
    params['difficulty'] = mode.get('difficulty')


  names = {t.get('name') for t in table}
  values = []
  if mode.get('type') == 'raid':
    val = wcl.getReportCodesFromRanksZone(params)
    values = {k: lst
              for k,v in val.items()
              if (lst := list(filter(lambda x: x.get('name') in names, v)))
              if lst != []
              }
  if mode.get('type') == 'm+':
    values = wcl.getReportCodesFromRanks(params)

  # if mode.get('difficulty') == 4:
  #   raise SystemExit
  return {
    k: v
    for k, v in values.items()
    if k != 'dPqh2MG3npDLazKy'
  }


def process_analyzer(analyzer, MP, mode):
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
  reports = gen_report_dict(mode)
  keys = list(reports.keys())[:10]
  # keys = list(reports.keys())[: 4]
  report_dict = {k: v for k, v in reports.items() if k in keys}

  values = []

  if not MP:
    values = analyzer(report_dict)

  if MP:
    values = multiprocess_cb(analyzer, report_dict)

  return values


def format_num(num):
  from math import log
  suff = ' kmbt'
  digits = log(num, 10)//1
  if digits//3:
    return f"{num/(10**digits):.2f}{suff[int(digits//3)]}"
  return f"{num}"

global MAXHP
MAXHP = 12*10**5
def tick_magnitude_analyzer():
  def plot(ax, y, x, info, values, bins):
    if values == []:
      return
    if not y:
      ax[x, y].set_ylabel(info.get('name'))
    xlabel = []
    if info.get('type') == 'm+':
      if 'bracket' in info.keys():
        xlabel.append(f"key level: {info.get('bracket')+1}")
      else:
        xlabel.append("key level: max")
    if not x:
      ax[x, y].xaxis.set_label_position('top')
      if info.get('difficulty') == 3:
        ax[x, y].set_xlabel('raid difficulty: normal')
      if info.get('difficulty') == 4:
        ax[x, y].set_xlabel('raid difficulty: heroic')
      if info.get('difficulty') == 5:
        ax[x, y].set_xlabel('raid difficulty: mythic')
    if x + 1 == len({k.get('name') for k in table}):
      ax[x, y].set_xlabel(' '.join(xlabel))
    # ax[x, y].get_xaxis().set_ticks([])
    # ax[x, y].get_yaxis().set_ticks([])
    ax[x, y].hist(values, bins)
    for t in range(0, max(bins), MAXHP):
      ax[x, y].axvline(t, color='green')

  def plot_table():
    import matplotlib.pyplot as plt
    plt.style.use('dark_background')
    width = max(sum(1 for k in table if k.get('name') == j.get('name')) for j in table)
    height = len({k.get('name') for k in table})
    fig, ax = plt.subplots(height, 2*width)
    fig.suptitle("Stagger Tick Magnitude Distribution by Encounter/Instance", fontsize=16)
    fig.text(s="Full MaxHP / 2 Domain, Equal Bin Size", x=1/4, y=29/32, fontsize=16, ha='left', va='bottom')
    fig.text(s="Default UI MaxHP / 20 Domain, Low+Moderate+High+Unknown Bins", x=5/9, y=29/32, fontsize=16, ha='left', va='bottom')
    # fig.suptitle("x", fontsize=12, x=100, y=200, ha='left', va='bottom')
    # fig.suptitle("y", fontsize=12, x=100, y=200, ha='left', va='bottom')
    for index, info in enumerate(table):
      print(info)
      x = index % width
      y = (index - x) // width
      values = process_analyzer(window_analyzer, False, info) or []
      plot(ax, x, y, info, values, range(0, 10*MAXHP, MAXHP//10))
      plot(ax, x+width, y, info, values, range(0, 5*MAXHP//3, MAXHP//3))
    fig.set_size_inches(height*4, width*2*4)
    fig.savefig('out.png', dpi=400, bbox_inches="tight")

  def window_analyzer(report_dict, pipe=None):
    def process_tick(self, event):
      assert event.get('type') == 'damage'
      assert event.get('sourceID') is not None
      assert event.get('sourceID') == event.get('targetID')
      assert event.get('abilityGameID') == 124255
      assert event.get('hitType') == 1
      assert not event.get('isAoE')
      assert event.get('tick')
      self.event_data.append(event.get('amount', 0) + event.get('absorbed', 0))
      # bl = ['timestamp', 'type', 'sourceID', 'targetID', 'abilityGameID', 'fight', 'hitType', 'isAoE', 'tick', 'targetMarker', 'sourceMarker']
      # for k, v in event.items():
      #   if k not in bl:
      #     print(k, v, end=' ')
      # print()

    rv = Analyzer(
      report_dict.keys(),
      per_fight_analysis=False,
      fight_filter=gen_fight_filter(report_dict),
      fight_params_update=gen_fight_params_update(report_dict),
      params={'limit': 25000, 'filterExpression': "ability.id=124255 and type='damage'"},
      callbacks=[
        {'any': True, 'callback': process_tick},
      ],
      event_data=[]
    )

    if pipe is not None:
      pipe.send(rv.event_data)
    else:
      return rv.event_data

  plot_table()
