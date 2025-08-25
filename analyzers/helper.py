import wcl
from copy import deepcopy

__all__ = ['report_code_to_events', 'flatten_event_data', 'Analyzer']
# not happy with how this function feels to use, but it greatly improves
# writing nearly all analyzers as the pattern is quite repetitive
# TODO: Improve interface with method


def report_code_to_events(
  report_codes, params_base, fight_filter, event_data_base, callbacks
):
  # package up all event_data objects per fight analyzed to be returned by this method
  # add params to event_data_base so params can be used in callbacks without passing it explicitly
  event_datum = {report_code: {} for report_code in report_codes}
  event_data_local = deepcopy(event_data_base)
  event_data_local.update({'params': params_base})

  for report_id, report_code in enumerate(report_codes):
    # if report_id != 1:
    #   continue
    # report points used
    # update params to include:
    # - report code
    # - initialized start and end timestamps to large values (0, 1e100)
    # gather fights in report code
    params, fights = report_to_fights(report_code, params_base, fight_filter)

    for fight_id, fight in enumerate(fights):
      # if fight_id != 5:
      #   continue
      # update params to include:
      # - corrected start and end timestamps for fight
      # gather events from fight
      # make a copy of event_data_base to be used for this fight
      # attach events for fight to event_data
      # add reference to event_data to event_datum
      params, events = fight_to_events(params, fight_id, fight)
      event_data = deepcopy(event_data_local)
      event_data.update({'events': events})
      event_datum[report_code].update({fight_id: event_data})

      for event_id, event in enumerate(events):
        # update event_id field so we have current event array position
        # iterate over callbacks.
        # if all filter parameters match, execute callback(s)
        # if 'any': True filter exists, execute callback(s)
        # if no callbacks were run, execute 'otherwise': True callback(s)
        event_data.update({'event_id': event_id})
        callbacks_executed = [
          callback.get( 'callback', lambda *_: None )( event, event_data )
          for callback in callbacks
          if all( [
              event.get( key ) == value
              for key, value in callback.items()
              if key != 'callback'
          ] ) or callback.get( 'any' )
        ]  # yapf: disable
        if len(callbacks_executed) < 1:
          [
            callback.get('callback', lambda *_: None)(event, event_data)
            for callback in callbacks
            if callback.get('otherwise')
          ]
    #   if fight_id == 5:
    #     break
    # break
  return event_datum


def fight_duration(fight):
  return fight.get('endTime') - fight.get('startTime')


def report_to_fights(report_code, param_base, fight_filter):
  print('===================================')
  print('report code:', report_code)
  wcl.getPointsSpent()
  print('===================================')
  min_fight_duration = 10000
  param_base.update({'code': report_code, 'startTime': 0, 'endTime': 1e100})
  return param_base, [
    fight
    for fight in wcl.getFights( param_base )
    if fight_filter( fight ) and fight_duration( fight ) > min_fight_duration
  ]  # yapf: disable


def fight_to_events(params, fight_id, fight):
  print(fight_id + 1)
  params.update({'startTime': fight.get('startTime'), 'endTime': fight.get('endTime')})
  return params, wcl.getEvents(params)


# given the typical return shape of report_code_to_events event_data, flatten
# it to look like event_data_base
def flatten_event_data(event_data, event_data_base):
  return {
    key: [
      value
      for report_code in event_data.values()
      for fight_data in report_code.values()
      for source_key, elements in fight_data.items()
      if isinstance(elements, list)
      if source_key == key and source_key in event_data_base.keys()
      for value in elements
    ]
    for key in event_data_base.keys()
  }


class Analyzer:
  def update_params(self, update, update_fn=None):
    self.params.update(update)
    if update_fn is not None:
      update_fn_data = update_fn(self) or {}
      self.params.update(update_fn_data)
      return True
    return True

  def default_fight_filter(self, fight_data):
    assert isinstance(fight_data, dict), 'fight_data must be a dict'
    start_time = fight_data.get('startTime', 0)
    end_time = fight_data.get('endTime', 1e100)
    return end_time - start_time > 1e3 * 10

  def print_fight_info(self):
    print(f'report code: {self.report_code} | fight id: {self.fight_id}')
    return True

  def update_analyzer(self, report_code, fight_data, fight_id):
    if self.per_fight_analysis:
      self.event_data = deepcopy( self.event_data_base )  # yapf: disable
    self.report_code = report_code
    self.fight_data = fight_data
    self.fight_id = fight_id
    return True

  def process_events(self):
    self.events = wcl.getEvents(self.params)
    self.pre_process(self)
    for event_id, event in enumerate(self.events):
      if self.skip_to_next_fight:
        break
      self.event_id = event_id
      self.execute_callbacks(event)
    self.skip_to_next_fight = False
    self.post_process(self)
    return True

  def execute_callbacks(self, event):
    executed_callbacks = [
      callback.get( 'callback', lambda *_: True )( self, event )
      for callback in self.callbacks
      if callback.get( 'any' ) or all( [
          event.get( key ) == value or isinstance( value, list ) and event.get( key ) in value
          for key, value in callback.items()
          if key != 'callback'
      ] )
    ]  # yapf: disable
    if len(executed_callbacks) < 1:
      [
        callback.get( 'callback', lambda *_: True )( self, event )
        for callback in self.callbacks
        if callback.get( 'otherwise' )
      ]  # yapf: disable

  def __init__(self, report_codes, **kwargs):
    self.kwargs = kwargs
    self.params = self.kwargs.get('params', {})
    self.event_data_base = self.kwargs.get('event_data', {})
    self.report_params_update = self.kwargs.get('report_params_update', lambda *_: {})
    self.fight_params_update = self.kwargs.get('fight_params_update', lambda *_: {})
    self.custom_fight_filter = self.kwargs.get('fight_filter', lambda *_: True)
    self.callbacks = self.kwargs.get('callbacks', [])
    self.pre_process = self.kwargs.get('preprocess', lambda *_: {})
    self.post_process = self.kwargs.get('postprocess', lambda *_: {})

    self.skip_to_next_fight = False
    self.per_fight_analysis = self.kwargs.get('per_fight_analysis', False)

    if self.per_fight_analysis:
      self.data = [
        {
          'report_code': report_code,
          'fight_id': self.fight_id,
          'event_data': self.event_data
        }
        for report_code in report_codes
        # if wcl.getPointsSpent() or True
        if self.update_params( { 'code': report_code }, self.report_params_update )
        for fight_data in wcl.getFights( self.params )
        if self.default_fight_filter( fight_data )
        if self.update_analyzer( report_code, fight_data, fight_data.get( 'id', -1 ) )
        if self.custom_fight_filter( self, fight_data )
        if self.update_params( {
            'startTime': fight_data.get( 'startTime' ),
            'endTime': fight_data.get( 'endTime' )
        }, self.fight_params_update )
        if self.print_fight_info()
        if self.process_events()
      ]  # yapf: disable
    else:
      self.event_data = self.event_data_base
      [
        report_code
        for report_code in report_codes
        # if wcl.getPointsSpent() or True
        if self.update_params( { 'code': report_code }, self.report_params_update )
        for fight_data in wcl.getFights( self.params )
        if self.default_fight_filter( fight_data )
        if self.update_analyzer( report_code, fight_data, fight_data.get( 'id', -1 ) )
        if self.custom_fight_filter( self, fight_data )
        if self.update_params( {
            'startTime': fight_data.get( 'startTime' ),
            'endTime': fight_data.get( 'endTime' )
        }, self.fight_params_update )
        if self.print_fight_info()
        if self.process_events()
      ]  # yapf: disable

    # wcl.getPointsSpent()
