import math


class bcolors:
  GREEN = '\033[92m'
  RED = '\033[91m'
  ENDC = '\033[0m'

  RED_B = '\033[41m'

  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKCYAN = '\033[96m'
  WARNING = '\033[93m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'


def t(ms):
  seconds = ms / 1000
  minutes = math.floor(seconds / 60)
  hours = math.floor(minutes / 60)
  remainder = seconds - 60 * (minutes + 60 * hours)
  sec = math.floor(remainder)
  dec = str(round(remainder - sec, 3))[2:]
  return '{hours:0=2}:{minutes:0=2}:{sec:0=2}.{dec:0<3}'.format(
    hours=hours, minutes=minutes, dec=dec, sec=sec
  )


def isID(event, id):
  return event.get('abilityGameID') == id


class Stagger:
  def __init__(self, data):
    self.data = data
    self.tick_count = 20
    self.p = 1
    self.b = 1
    self.reorder = 0
    self.k = 11766 * 1.253

    self.agi = 8335
    self.multipliers = 1.05

    self.pool = 0
    self.tick = 0
    self.remainder = 0

    self.types = {}

    self.invalid_hit_types = [
      0,  # miss
      7,  # dodge
      8,  # parry
      2,  # dodge
    ]

    self.hit_types = {}

  def fmt(self, v):
    if self.b:
      return f'{round(v, 1)}'
    vals = 'kmbt'
    digits = math.floor(math.log10(v))
    index = math.floor(digits / 3)
    if index > 0:
      return f'{round(v / 10 ** (index * 3), 1)}{vals[index - 1]}'
    return f'{round(v, 1)}'

  def stagger_p(self, event):
    is_magic = 1.0
    if not isID(event, 1):
      is_magic = 0.45
    base = self.multipliers * self.agi
    return base / (base + self.k) * is_magic

  def print(self, event):
    match event.get('type'):
      case 'damage':
        if not isID(event, 124255):
          timestamp = t(event.get('timestamp'))
          amount = self.fmt(
            (event.get('amount', 0) + event.get('absorbed', 0)) * self.stagger_p(event)
          )
          pool = self.fmt(self.pool)
          print(
            f'{self.index:<4} {bcolors.GREEN}a{bcolors.ENDC}: {timestamp:<15} {amount:<10} {pool:<10}'
          )
        if isID(event, 124255):
          timestamp = t(event.get('timestamp'))
          amount = self.fmt(event.get('unmitigatedAmount'))
          tick = self.fmt(math.ceil(self.tick + self.tick_adjust))
          if amount == tick:
            print(
              f'{self.index:<4} {bcolors.RED}t{bcolors.ENDC}: {timestamp:<15} {amount:<10} {tick:<10}'
            )
          else:
            print(
              f'{self.index:<4} {bcolors.RED}t{bcolors.ENDC}: {bcolors.RED_B}{timestamp:<15} {amount:<10} {tick:<10}{bcolors.ENDC}'
            )

  def reset(self):
    self.pool = 0
    self.tick = 0
    self.remainder = 0
    self.tick_adjust = 0

  def process(self):
    self.index = 0
    self.reset()
    while self.index < len(self.data):
      event = self.data[self.index]
      self.types[event.get('type')] = self.types.get(event.get('type'), 0) + 1
      match event.get('type'):
        case 'damage':
          self.hit_types[event.get('hitType', None)] = (
            self.hit_types.get(event.get('hitType'), 0) + 1
          )
          if (
            not isID(event, 124255)
            and event.get('hitType', 0) not in self.invalid_hit_types
          ):
            amount = (
              event.get('amount', 0) + event.get('absorbed', 0)
            ) * self.stagger_p(event)
            self.pool += amount
            self.remainder = 0
            self.tick = math.floor(self.pool / self.tick_count)
            self.remainder = self.pool - self.tick * self.tick_count
            if self.remainder > 1:
              self.tick_adjust = 1
            if self.p:
              self.print(event)
          if isID(event, 124255):
            self.pool -= self.tick + self.tick_adjust
            if self.p:
              self.print(event)
            dist = (event.get('unmitigatedAmount') - self.tick - self.tick_adjust) ** 2
            if dist > 32 and self.reorder:
              print(f'REORDER DETECTED AS {dist}>4')
              for x in range(self.index, -1, -1):
                if self.data[x].get('type') == 'absorbed':
                  if self.data[x].get('timestamp') != self.data[self.index].get(
                    'timestamp'
                  ):
                    print(f'FAILED TO REORDER AT {self.index}, {x}')
                    return
                  print(f'REORDERING {x} WITH {self.index}')
                  self.data[x], self.data[self.index] = (
                    self.data[self.index],
                    self.data[x],
                  )
                  self.index = 0
                  self.reset()
                  break
              continue
            if self.remainder >= 1:
              self.remainder -= self.tick_adjust
            else:
              self.tick_adjust = 0
      self.index += 1
