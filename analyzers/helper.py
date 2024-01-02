import wcl
from copy import deepcopy

__all__ = ["report_code_to_events"]
# not happy with how this function feels to use, but it greatly improves
# writing nearly all analyzers as the pattern is quite repetitive
# TODO: Support multiple callback fields and sets of callbacks
# TODO: Improve interface with method

def report_code_to_events(
  report_codes,
  params_base,
  fight_filter,
  event_data_base,
  callbacks,
  callback_field
):
  # package up all event_data objects per fight analyzed to be returned by this method
  # add params to event_data_base so params can be used in callbacks without passing it explicitly
  event_datum = {
    report_code: {}
    for report_code in report_codes
  }
  event_data_base.update( {
    'params': params_base
  } )

  for report_code in report_codes:
    # report points used
    # update params to include:
    # - report code
    # - initialized start and end timestamps to large values (0, 1e100)
    # gather fights in report code
    params, fights = report_to_fights( report_code, params_base, fight_filter )

    for fight_id, fight in enumerate( fights ):
      # update params to include:
      # - corrected start and end timestamps for fight
      # gather events from fight
      # make a copy of event_data_base to be used for this fight
      # add reference to event_data to event_datum
      params, events = fight_to_events( params, fight_id, fight )
      event_data = deepcopy( event_data_base )
      event_datum[ report_code ].update( {
        fight_id: event_data
      } )

      for event in events:
        # find the key used in callback dict
        # capture callback from callback dict
        # execute callback using event and event_data
        callback_field_value = event.get( callback_field )
        callback = callbacks.get( callback_field_value, lambda *x: x )
        callback( event, event_data )
  return event_datum

def fight_duration( fight ):
  return fight.get( 'endTime' ) - fight.get( 'startTime' )

def report_to_fights( report_code, param_base, fight_filter ):
  print( '===================================' )
  print( 'report code:', report_code )
  wcl.getPointsSpent()
  print( '===================================' )
  min_fight_duration = 1000
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
