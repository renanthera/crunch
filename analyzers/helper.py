import wcl
from copy import deepcopy

__all__ = [ "report_code_to_events", "flatten_event_data" ]
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
