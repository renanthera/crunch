import json
from .helper import *
from dataclasses import dataclass, field
import wcl


@dataclass
class Point:
  from_source: bool = False
  from_target: bool = False
  x: int = 0
  y: int = 0

  def __str__(self):
    return f'({self.x}, {self.y})'


@dataclass
class Screen:
  points: list[Point] = field(default_factory=list)

  def post_init(self):
    self.x_max = max([point.x for point in self.points if point.x])
    self.x_min = min([point.x for point in self.points if point.x])
    self.width = self.x_max - self.x_min
    self.y_max = max([point.y for point in self.points if point.y])
    self.y_min = min([point.y for point in self.points if point.y])
    self.height = self.y_max - self.y_min

    self.ratio = 1000 / self.width

    # t.screensize(self.width, self.height)

  def transform(self, point: Point):
    return Point(
      point.from_source,
      point.from_target,
      int((self.x_max - point.x) * self.ratio),
      int((self.y_max - point.y) * self.ratio),
    )


def init_targets(self, _):
  targets = [
    entity
    for entity in wcl.getMasterData(self.params)
    if entity.get('gameID') == self.params.get('zzz_boss_id')
  ]
  self.event_data = [
    {
      'id': target.get('id'),
      'name': target.get('name'),
      'reportcode': self.params.get('reportcode'),
      'points': [],
    }
    for target in targets
  ]
  # print(self.event_data)
  # print(targets)
  # raise SystemExit


def process_movement(self, event):
  if event.get('type') == 'encounterstart':
    return

  source_id = event.get('sourceID')
  target_id = event.get('targetID')
  targets = [target.get('id') for target in self.event_data]
  source_in_targets = source_id in targets
  target_in_targets = target_id in targets
  assert source_in_targets or target_in_targets
  key = source_id if source_in_targets else target_id
  indices = [
    index for index, value in enumerate(self.event_data) if value.get('id') == key
  ]
  index = indices[0]

  x = event.get('x', 0)
  y = event.get('y', 0)
  point = Point(source_in_targets, target_in_targets, x, y)
  self.event_data[index]['points'].append(point)
  # if point.x and point.y and point.from_target:
  #   print(point.from_source, point.from_target, point)
  #   print(json.dumps(event, indent=2))
  # raise SystemExit


def fight_filter(self):
  is_encounter = self.fight_data.get('encounterID') == self.params.get('encounterID')
  is_difficulty = self.fight_data.get('difficulty') == self.params.get('difficulty')
  is_kill = self.fight_data.get('kill') == True
  return is_encounter and is_difficulty and is_kill


def draw_path(report_codes, target_id, params):
  boss_id = target_id
  encounterID = params.get('encounterID', -1)
  difficulty = params.get('difficulty', 5)
  a = Analyzer(
    report_codes,
    params={
      'includeResources': True,
      'filterExpression': f"target.id={boss_id} or source.id={boss_id} or type='encounterstart'",
      'encounterID': encounterID,
      'limit': 25000,
      'difficulty': difficulty,
      'zzz_boss_id': boss_id,
    },
    callbacks=[
      {'type': 'damage', 'callback': process_movement},
      {'type': 'encounterstart', 'callback': init_targets},
    ],
    fight_filter=fight_filter,
    event_data=dict(),
  )

  import matplotlib.pyplot as plot

  plot.style.use('dark_background')
  fig, ax = plot.subplots(3, 3)
  for index, fight in enumerate(a.data):
    for target in fight['event_data']:
      points = target.get('points', [])
      screen = Screen(points)
      previous = None
      filtered_points = [
        point
        for point in points
        if (point.x and point.y and point.from_target)
        if (previous != point)
        if (previous := point) and True
      ]
      ax[index // 3, index % 3].set_title(fight['report_code'])
      ax[index // 3, index % 3].set(xlabel='', ylabel='')
      ax[index // 3, index % 3].plot(
        [point.x for point in filtered_points],
        [point.y for point in filtered_points],
        linewidth=2,
      )
  plot.show()
