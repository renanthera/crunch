from .helper import *

from math import sqrt
import matplotlib.pyplot as plot

def count_nearby_hits( event, event_data ):
  event_id = event_data.get( 'event_id' )
  events = event_data.get( 'events' )
  timestamp = event.get( 'timestamp' )
  spell_id = event.get( 'abilityGameID' )
  hits = []

  for e_next in events[ event_id: ]:
    if e_next.get( 'abilityGameID' ) == spell_id and not e_next.get( 'skip' ) and e_next.get( 'type' ) == 'damage' and e_next.get( 'timestamp' ) - timestamp < 5:
      hits.append( e_next )
      e_next[ 'skip' ] = True
    if e_next.get( 'timestamp' ) - timestamp > 5:
      break
  return hits

def get_total_amount( event ):
  return event.get( 'amount', 0 ) + event.get( 'absorbed', 0 ) + event.get( 'overkill', 0 )

def sqrt_scaling( count, threshold ):
  if count < threshold:
    return 1
  return sqrt( threshold / count )

def crit( event ):
  return event.get('hitType') == 2 and 2 or 1

def ks_callback( event, event_data ):
  hits = count_nearby_hits( event, event_data )
  hit_count = len( hits )
  event_data[ 'ks_events' ].extend( [
    get_total_amount( hit ) / sqrt_scaling( hit_count, 5 ) / crit( hit )
    for hit in hits
  ] ) # yapf: disable

def rsk_callback( event, event_data ):
  event_data['rsk_events'].append( get_total_amount( event ) / crit( event ) )

def noop( *_ ):
  return

def damage( reportCodes ):
  event_data_base = {
    'ks_events': [],
    'rsk_events': []
  }
  data = report_code_to_events(
    reportCodes,
    {
      'filterExpression': 'ability.id in (185099, 121253)'
    },
    lambda fight: fight,
    event_data_base,
    [ {
      'abilityGameID': 185099,
      'type': 'damage',
      'callback': rsk_callback
    },
      {
        'abilityGameID': 121253,
        'type': 'damage',
        'callback': ks_callback
      } ]
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

  flat = flatten_event_data( data, event_data_base )

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

  _, ax = plot.subplots(ncols=len(data) * 2, nrows=max([ len(report_data) for report_data in data.values()]))
  for report_index, (report_code, report_data) in enumerate(data.items()):
    for fight_index, fight_data in report_data.items():
      for index, (key, value) in enumerate({
          key: value
          for key, value in fight_data.items()
          if key in event_data_base.items()
      }):
        print(value)
        ax[report_index + index, fight_index].hist(
          value,
          bins=128,
          linewidth=0.5,
          label=f'{report_code} {fight_index} {key}',
          alpha=0.7
        )

  plot.show()

  # print(aggregate)
