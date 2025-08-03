from matplotlib.colors import rgb_to_hsv
import wcl
from .helper import Analyzer
from collections import defaultdict
from collections.abc import Callable
from typing import Any

class hashdict(dict):
  def __hash__(self):
    return hash((frozenset(self), frozenset(self.values())))

def execute_queue(behaviours):
  rvs = {}
  for b in behaviours:
    if b.requirement is None:
      yield b.is_applicable(None)
    elif b.requirement in rvs.keys():
      yield b.is_applicable(rvs[b.requirement])
    else:
      rvs.update({b.requirement: b.execute_requirement()})
      yield b.is_applicable(rvs[b.requirement])

class Behaviour:
  requirement = None

  # override this
  def requirements(self, params):
    return (wcl.getPlayerDetails, hashdict(params))

  # override this
  def is_applicable(self, requirement):
    return False

  # override this
  def validate(self, events):
    pass

  def configure(self, analyzer):
    if self.requirements(analyzer) is not None:
      self.requirement = self.requirements(analyzer)

  def execute_requirement(self):
    if self.requirement is not None:
      return self.requirement[0](self.requirement[1])
    return None

def check_behaviour(params):
  behaviours = [Behaviour() for _ in range(20)]

  def _fight_filter(data):
    for b in behaviours:
      b.configure(data.params)
    return any(execute_queue(behaviours))

  assert('guildID' in params)
  codes = [entry.get('code') for entry in wcl.getReportCodes( params )]
  if params.get('report_limit') is not None:
    codes = codes[:params.get('report_limit')]


  # print(v.requirements)
  _ = Analyzer(
    codes,
    params = {
      'limit': 25000,
    },
    callbacks = [
      {
        'any': False,
        'callback': lambda _, e: print(e)
      }
    ],
    fight_filter = _fight_filter
  )
