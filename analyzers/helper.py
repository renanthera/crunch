import wcl
from copy import deepcopy

__all__ = [ "report_code_to_events", "flatten_event_data", "Analyzer" ]
# not happy with how this function feels to use, but it greatly improves
# writing nearly all analyzers as the pattern is quite repetitive
# TODO: Improve interface with method

def report_code_to_events( report_codes, params_base, fight_filter, event_data_base, callbacks ):
  # package up all event_data objects per fight analyzed to be returned by this method
  # add params to event_data_base so params can be used in callbacks without passing it explicitly
  event_datum = {
    report_code: {}
    for report_code in report_codes
  }
  event_data_local = deepcopy(event_data_base)
  event_data_local.update( {
    'params': params_base
  } )

  for report_id, report_code in enumerate( report_codes ):
    # if report_id != 1:
    #   continue
    # report points used
    # update params to include:
    # - report code
    # - initialized start and end timestamps to large values (0, 1e100)
    # gather fights in report code
    params, fights = report_to_fights( report_code, params_base, fight_filter )


    for fight_id, fight in enumerate( fights ):
      # if fight_id != 5:
      #   continue
      # update params to include:
      # - corrected start and end timestamps for fight
      # gather events from fight
      # make a copy of event_data_base to be used for this fight
      # attach events for fight to event_data
      # add reference to event_data to event_datum
      params, events = fight_to_events( params, fight_id, fight )
      event_data = deepcopy( event_data_local )
      event_data.update( {
        'events': events
      } )
      event_datum[ report_code ].update( {
        fight_id: event_data
      } )


      for event_id, event in enumerate( events ):
        # update event_id field so we have current event array position
        # iterate over callbacks.
        # if all filter parameters match, execute callback(s)
        # if 'any': True filter exists, execute callback(s)
        # if no callbacks were run, execute 'otherwise': True callback(s)
        event_data.update( {
          'event_id': event_id
        } )
        callbacks_executed = [
          callback.get( 'callback', lambda *_: None )( event, event_data )
          for callback in callbacks
          if all( [
              event.get( key ) == value
              for key, value in callback.items()
              if key != 'callback'
          ] ) or callback.get( 'any' ) == True
        ] # yapf: disable
        if len( callbacks_executed ) < 1:
          [
            callback.get( 'callback', lambda *_: None )( event, event_data )
            for callback in callbacks
            if callback.get( 'otherwise' ) == True
          ]
    #   if fight_id == 5:
    #     break
    # break
  return event_datum

def fight_duration( fight ):
  return fight.get( 'endTime' ) - fight.get( 'startTime' )

def report_to_fights( report_code, param_base, fight_filter ):
  print( '===================================' )
  print( 'report code:', report_code )
  wcl.getPointsSpent()
  print( '===================================' )
  min_fight_duration = 10000
  param_base.update( {
    'code': report_code,
    'startTime': 0,
    'endTime': 1e100
  } )
  return param_base, [
    fight
    for fight in wcl.getFights( param_base )
    if fight_filter( fight ) and fight_duration( fight ) > min_fight_duration
  ] # yapf: disable

def fight_to_events( params, fight_id, fight ):
  print( fight_id + 1 )
  params.update( {
    'startTime': fight.get( 'startTime' ),
    'endTime': fight.get( 'endTime' )
  } )
  return params, wcl.getEvents( params )

# given the typical return shape of report_code_to_events event_data, flatten
# it to look like event_data_base
def flatten_event_data( event_data, event_data_base ):
  return {
    key: [
      value
      for report_code in event_data.values()
      for fight_data in report_code.values()
      for source_key, elements in fight_data.items()
      if isinstance( elements, list )
      if source_key == key and source_key in event_data_base.keys()
      for value in elements
    ]
    for key in event_data_base.keys()
  }

#
class Analyzer:

  def print_fight_info( self, report_code ):
    self.fight_count += 1
    print( f'report code: {report_code} | fight id: {self.fight_count}')
    return True

  def default_fight_filter( self, fight_data ):
    assert isinstance( fight_data, dict ), 'fight_data must be a dict'
    start_time = fight_data.get( 'startTime', 0 )
    end_time = fight_data.get( 'endTime', 1e100 )
    return end_time - start_time > 1e3 * 10

  def update_params( self, update ):
    self.kwargs.get( 'params', {} ).update( update )
    return True

  def update_event_data( self ):
    self.event_data = deepcopy( self.kwargs.get( 'event_data', {} ) )
    return True

  def process_events( self ):
    for event_id, event in enumerate( wcl.getEvents( self.kwargs.get( 'params' ) ) ):
      self.execute_callbacks( event, event_id )
    return True

  def execute_callbacks( self, event, event_id ):
    event_data = self.event_data | { 'event_id': event_id }
    executed_callbacks = [
      callback.get( 'callback', lambda *_: True )( self, event, event_data )
      for callback in self.kwargs.get( 'callbacks', [] )
      if all( [
          event.get( key ) == value
          for key, value in callback.items()
          if key != 'callback'
      ] ) or callback.get( 'any' ) == True
    ]
    if len( executed_callbacks ) < 1:
      [
        callback.get( 'callback', lambda *_: True )( self, event, event_data )
        for callback in self.kwargs.get( 'callbacks', [] )
        if callback.get( 'otherwise' ) == True
      ]

  def __init__( self, report_codes, **kwargs ):
    self.report_codes = report_codes
    self.kwargs = kwargs
    self.fight_count = 0

    # for each fight id in each report code
    # - filter fights in fight_data based on user-defined function and default_fight_filter
    # - print report code and self.fight_count
    # - update parameters with fight start and end
    # - make a copy of event_data
    # - process events in fight with callbacks via process_events and execute_callbacks
    self.data = [
      {
        'report_code': report_code,
        'fight_id': fight_id,
        'event_data': self.event_data
      }
      for report_code in report_codes
      if self.update_params( { 'code': report_code } )
      for fight_id, fight_data in enumerate( wcl.getFights( self.kwargs.get( 'params', {} ) ) )
      if self.default_fight_filter( fight_data )
      if self.kwargs.get( 'fight_filter', lambda: True )( fight_data )
      if self.print_fight_info( report_code )
      if self.update_params( { 'startTime': fight_data.get( 'startTime' ), 'endTime': fight_data.get( 'endTime' ) } )
      if self.update_event_data()
      if self.process_events()
    ]
