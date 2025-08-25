from .helper import *

from math import sqrt
import matplotlib.pyplot as plot


def damage(reportCodes):
  def count_nearby_hits(event, event_data):
    event_id = event_data.get('event_id')
    events = event_data.get('events')
    timestamp = event.get('timestamp')
    spell_id = event.get('abilityGameID')
    hits = []

    for e_next in events[event_id:]:
      if (
        e_next.get('abilityGameID') == spell_id
        and not e_next.get('skip')
        and e_next.get('type') == 'damage'
        and e_next.get('timestamp') - timestamp < 5
      ):
        hits.append(e_next)
        e_next['skip'] = True
      if e_next.get('timestamp') - timestamp > 5:
        break
    return hits

  def get_total_amount(event):
    return event.get('amount', 0) + event.get('absorbed', 0) + event.get('overkill', 0)

  def sqrt_scaling(count, threshold):
    if count < threshold:
      return 1
    return sqrt(threshold / count)

  def crit(event):
    return event.get('hitType') == 2 and 2 or 1

  def ks_callback(event, event_data):
    hits = count_nearby_hits(event, event_data)
    hit_count = len(hits)
    event_data[ 'ks_events' ].extend( [
      get_total_amount( hit ) / sqrt_scaling( hit_count, 5 ) / crit( hit )
      for hit in hits
    ] )  # yapf: disable

  def rsk_callback(event, event_data):
    event_data['rsk_events'].append(get_total_amount(event) / crit(event))

  def noop(*_):
    return

  event_data_base = {'ks_events': [], 'rsk_events': []}
  data = report_code_to_events(
    reportCodes,
    {'filterExpression': 'ability.id in (185099, 121253)'},
    lambda fight: fight,
    event_data_base,
    [
      {'abilityGameID': 185099, 'type': 'damage', 'callback': rsk_callback},
      {'abilityGameID': 121253, 'type': 'damage', 'callback': ks_callback},
    ],
  )

  # import json
  # for report_code, report_data in data.items():
  #   print( report_code )

  #   for fight_id, fight_data in report_data.items():
  #     print( fight_id + 1 )
  #     for key, value in [
  #         (k, v)
  #         for k, v in fight_data.items()
  #         if k in event_data_base.keys()
  #     ]:
  #       if len( value ) > 0:
  #         print( '\t', key, '\t', sum( value ) / len( value ) )
  #         # print( json.dumps( ks, indent=2 ) )

  flat = flatten_event_data(data, event_data_base)

  # print(json.dumps(flat, indent=2))

  plot.style.use('dark_background')
  # _, ax = plot.subplots()
  # for key, value in flat.items():
  #   ax.hist(
  #     flat[key],
  #     bins=128,
  #     linewidth=0.5,
  #     label=key,
  #     alpha=0.7
  #   )

  _, ax = plot.subplots(
    ncols=len(data) * 2, nrows=max([len(report_data) for report_data in data.values()])
  )
  for report_index, (report_code, report_data) in enumerate(data.items()):
    for fight_index, fight_data in report_data.items():
      for index, (key, value) in enumerate(
        {
          key: value
          for key, value in fight_data.items()
          if key in event_data_base.items()
        }
      ):
        print(value)
        ax[report_index + index, fight_index].hist(
          value,
          bins=128,
          linewidth=0.5,
          label=f'{report_code} {fight_index} {key}',
          alpha=0.7,
        )

  plot.show()

  # print(aggregate)


def bug_detection(report_codes):
  import wcl
  import json

  damage_ids = [185099, 121253]
  cast_ids = [107428, 185099, 121253]
  buff_ids = [418361, 228563, 383800]

  def fight_params_update(self):
    players = [
      "'" + player.get('name', '') + "'"
      for player in wcl.getPlayersWithTalent(self.params, 418359)
    ]

    if not players:
      self.custom_fight_filter = lambda *_: False
      return {}
    self.custom_fight_filter = self.kwargs.get('fight_filter', lambda *_: True)

    player_names = ', '.join(players)
    clause_1 = f"type in ('applybuff', 'applybuffstack', 'refreshbuff', 'refreshbuffstack', 'removebuff', 'removebuffstack') and ability.id in ({', '.join(map(str, buff_ids))})"
    clause_2 = (
      f"type in ('damage') and ability.id in ({', '.join(map(str, damage_ids))})"
    )
    clause_3 = f"type in ('cast') and ability.id in ({', '.join(map(str, cast_ids))})"
    clause_4 = "type in ('dungeonstart', 'encounterstart')"

    return {
      'filterExpression': f'(source.name in ({player_names}) and (({clause_1}) or ({clause_2}) or ({clause_3}))) or ({clause_4})'
    }

  def pta_buff(self, event):
    previous_application = self.event_data['pta_stacks']
    last_stack = (
      previous_application['stack']
      if event.get('timestamp') - previous_application['timestamp'] < 20 * 1000
      else 0
    )
    self.event_data['pta_stacks'].update(
      {'stack': event.get('stack', last_stack), 'timestamp': event.get('timestamp')}
    )

  def other_buffs(self, event):
    buff_status = self.event_data['other_buffs'][event.get('abilityGameID')]['up']
    if event.get('type') == 'applybuff':
      assert buff_status == False, f'buff applied when it was already applied\n{event}'
      self.event_data['other_buffs'][event.get('abilityGameID')]['up'] = True
    if event.get('type') == 'refreshbuff':
      assert buff_status == True, (
        f'buff refreshed when it was not already applied\n{event}'
      )
      self.event_data['other_buffs'][event.get('abilityGameID')]['up'] = True
    if event.get('type') == 'removebuff':
      assert buff_status == True, (
        f'buff removed when it was not already applied\n{event}'
      )
      self.event_data['other_buffs'][event.get('abilityGameID')]['up'] = False
    self.event_data['other_buffs'][event.get('abilityGameID')]['timestamp'] = event.get(
      'timestamp'
    )

  def consume_pta(self, event):
    previous_application = self.event_data['pta_stacks']
    if previous_application['stack'] != 10:
      return
    self.event_data['pta_stacks'].update({'stack': 0})
    if event.get('timestamp') - previous_application['timestamp'] > 20 * 1000:
      return

    if any(
      [v.get('up') for k, v in self.event_data['other_buffs'].items() if k == 228563]
    ):
      self.event_data['pta_triggers_with_buff'] += 1
    self.event_data['pta_triggers'] += 1
    print('  pta triggered')
    print('  searching for pta trigger cast, starting at\n  ', end='')
    print_event(self, self.events[self.event_id + 1])
    for event_next in self.events[self.event_id + 1 :]:
      if event_next.get('timestamp') - event.get('timestamp') > 1000:
        self.event_data['pta_no_match'] += 1
        print('no match found')
        print_event(self, event)
        break
      if (
        event_next.get('type') == 'cast' and event_next.get('abilityGameID') in cast_ids
      ):
        print('  marking this event as triggered by pta:\n  ', end='')
        print_event(self, event_next)
        if not event_next.get('triggered_by_pta'):
          event_next.update(
            {'triggered_by_pta': True, 'trigger_timestamp': event.get('timestamp')}
          )
        break

  def check_buffs(self, event):
    if event.get('triggered_by_pta') and any(
      [
        v.get('up') and v.get('timestamp') < event.get('trigger_timestamp')
        for k, v in self.event_data['other_buffs'].items()
        if k == 228563
      ]
    ):
      # print( 'bug detected' )
      # print( self.event_data[ 'other_buffs' ] )
      # print_event( self, event )
      self.event_data['bug_counter'] += 1

  def fmt_timestamp(timestamp):
    timestamp_s = timestamp // 1000
    timestamp_m = timestamp_s // 60
    timestamp_h = timestamp_m // 60
    return f'{timestamp_h % 60:02}:{timestamp_m % 60:02}:{timestamp_s % 60:02}.{timestamp % 1000:03}'

  def print_event(self, event):
    timestamp = event.get('timestamp') - self.fight_data.get('startTime')
    print(
      fmt_timestamp(timestamp),
      {key: value for key, value in event.items() if key != 'timestamp'},
    )

  analyzer = Analyzer(
    report_codes,
    fight_filter=lambda s: s.fight_id == 3,
    callbacks=[
      # {
      #   'any': True,
      #   'callback': lambda s, e: print( e.get('sourceID'))
      # },
      {
        'abilityGameID': [228563, 383800],  # , 383800
        'type': ['applybuff', 'refreshbuff', 'removebuff'],
        'callback': other_buffs,
      },
      {
        'abilityGameID': 418361,
        'type': ['applybuff', 'applybuffstack', 'refreshbuff', 'refreshbuffstack'],
        'callback': pta_buff,
      },
      {'abilityGameID': damage_ids, 'type': 'damage', 'callback': consume_pta},
      {'abilityGameID': cast_ids, 'type': 'cast', 'callback': check_buffs},
    ],
    event_data={
      'pta_stacks': {'stack': 0, 'timestamp': 0},
      'other_buffs': {
        228563: {'up': False, 'timestamp': 0},
        383800: {'up': False, 'timestamp': 0},
      },
      'bug_counter': 0,
      'pta_triggers': 0,
      'pta_triggers_with_buff': 0,
      'pta_no_match': 0,
    },
    params={
      'limit': 25000,
    },
    fight_params_update=fight_params_update,
  )

  print(json.dumps(analyzer.data, indent=2))
