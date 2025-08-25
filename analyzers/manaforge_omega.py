from .helper import *
import wcl


def shorten_number(num):
  from math import log

  suff = ' kmbg'
  index = log(num) / log(10) // 3
  divisor = 100 ** (index + 1)
  val = round(num / divisor, 1)
  return f'{val}{suff[int(index)]}'


def fmt_timestamp(timestamp):
  timestamp_s = timestamp // 1000
  timestamp_m = timestamp_s // 60
  timestamp_h = timestamp_m // 60
  return f'{timestamp_h % 60:02}:{timestamp_m % 60:02}:{timestamp_s % 60:02}.{timestamp % 1000:03}'


def plexus_sentinel():
  def _fight_filter(self, fight_data):
    return fight_data.get('encounterID') == 3129 and fight_data.get('difficulty') == 5

  def _print_event(self, event):
    # immune
    if event.get('amount') == 0:
      return

    if event.get('unmitigatedAmount') >= 8000000:
      print('BAD ', end=' ')
    else:
      print('GOOD', end=' ')

    timestamp = event.get('timestamp') - self.params.get('startTime')
    print(fmt_timestamp(timestamp), end=' ')

    print(
      wcl.getPlayerFromID(event.get('targetID'), self.params),
      shorten_number(event.get('unmitigatedAmount')),
    )

  codes = [
    report.get('code')
    for report in wcl.getReportCodes(
      {
        'guildID': 33026,
        'zoneID': 44,
        'pagination_limit': 5,
      }
    )
  ]

  data = Analyzer(
    codes,
    params={
      'limit': 25000,
      'filterExpression': 'ability.id = 1219346',
    },
    callbacks=[
      {
        'type': 'damage',
        'callback': _print_event,
        # 'callback': lambda _, e: print(e)
      }
    ],
    fight_filter=_fight_filter,
  )
