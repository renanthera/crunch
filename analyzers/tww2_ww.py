from .helper import *

rsk_cast = 107428
sck_cast = 101546
winning_streak_id = 1216182

def remove_buff(s, e):
  # print(e)
  s.event_data[e['sourceID']].update( {'consumed': True} )

def previous(s, e):
  id = e['sourceID']
  if id not in s.event_data.keys():
    s.event_data[id] = {e['abilityGameID']: 0, 'consumed': False}
  if s.event_data[id].get('consumed'):
    s.event_data[id][e['abilityGameID']] = s.event_data[id].get(e['abilityGameID'], 0) + 1
    s.event_data[id]['consumed'] = False

def counts( report_codes ):
  t = Analyzer(
    report_codes,
    params={
      'limit': 25000,
    },
    callbacks=[
      {
        'any': False,
        'callback': lambda _, u: print(u)
      },
      {
        'type': 'cast',
        'callback': previous
      },
      {
        'type': 'removebuff',
        'abilityGameID': winning_streak_id,
        'callback': remove_buff
      },
    ],
    event_data={})
  import json
  v = {}
  for fight in t.data:
    for actor, data in fight['event_data'].items():
      if v.get(actor) is None and len(data.items()) > 1:
        v.update({actor: {
          key: value
          for key, value in data.items()
          if key != 'consumed' and value > 0
        }})
        if len(v.get(actor, {}).items()) > 0:
          print(fight['report_code'], actor, v.get(actor))
        continue
      merge = {
        a: value
        for a, b in v.get(actor, {}).items()
        for c, d in data.items()
        if a == c and a != 'consumed'
        if b > 0 or d > 0
        if (value := b + d)
      }
      v.update({actor: merge})
      if len(v.get(actor, {}).items()) > 0:
        print(fight['report_code'], actor, v.get(actor))
