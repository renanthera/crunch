import wcl
from .helper import *

from math import sqrt

callbacks = [
  {
    'field': 'abilityGameID',
    'value': 185099,
    'callback': lambda e, e_d: e
  }
]

def count_nearby_hits( event, event_data ):
  event_id = event_data.get('event_id')
  events = event_data.get('events')
  timestamp = event.get('timestamp')
  spell_id = event.get('abilityGameID')
  count = 0

  for e_id, e_next in enumerate( events[event_id:] ):
    if e_next.get('abilityGameID') == spell_id and not e_next.get('skip') and e_next.get('type') == 'damage' and e_next.get('timestamp') - timestamp < 5:
      e_next['skip'] = True
      count += 1
    if e_next.get('timestamp') - timestamp > 5:
      break
  return count

def ks_callback( event, event_data ):
  event_id = event_data.get('event_id')
  events = event_data.get('events')
  timestamp = event.get('timestamp')
  spell_id = event.get('abilityGameID')
  count = count_nearby_hits( event, event_data )

  if count > 0:
    for e_id, e_next in enumerate( events[event_id:]):
      if e_next.get('abilityGameID') == spell_id and e_next.get('type') == 'damage' and e_next.get('timestamp') - timestamp < 5:
        amount = e_next.get('amount', 0) + e_next.get('absorbed', 0) + e_next.get('overkill', 0)
        event_data.get('ks_events').append(
          amount / sqrt( 5 / count )
        )

      if e_next.get('timestamp') - timestamp > 5:
        break


def damage( reportCodes ):
  data = report_code_to_events(
    reportCodes,
    {
      'filterExpression':
      'ability.id in (185099, 121253)'
    },
    lambda fight: fight,
    {
      'ks_events': [],
      'rsk_events': []
    },
    [
      {
        'abilityGameID': 185099,
        'type': 'damage',
        'callback': lambda e, e_d: e
      },
      {
        'abilityGameID': 121253,
        'type': 'damage',
        'callback': ks_callback
      }
    ]
  )

  for report_code, report_data in data.items():
    print(report_code)

    for fight_id, fight_data in report_data.items():
      if len(fight_data.get('ks_events')) > 0:
        print(fight_id, '\t', max(fight_data.get('ks_events')))
