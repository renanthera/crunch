class Query:
  # TODO: REWORK REQUEST
  parent = None
  cacheable = True

  def components( self ):
    pass

  def __init__( self, params, cacheable=None ):
    self.params = params.copy()
    self.tree = self.create_tree()
    self.string = self.stringify()
    self.cacheable = cacheable if cacheable is not None else self.cacheable

  def update( self, params ):
    assert len(params) == len(self.params), 'Updating params with the incorrect number of elements'
    assert set( params ) == set( self.params ), 'Updated keys do not match'
    assert all([ type(self.params.get(key)) is type(params.get(key)) or params.get(key) is None for key in self.params]), 'Types of values do not match'
    assert params != self.params, 'Params are unchanged'

    self.params.update( params )
    self.tree = self.create_tree()

  def create_tree( self ):
    self.params.update( {
      'children': self.components()
    } )

    if self.parent is None:
      return self.params.get( 'children' )
    return self.parent( self.params ).tree

  def stringify( self ):
    def recurse_nodes( node ):
      alias = node.get( 'alias' )
      name = node.get( 'name' )
      args = []
      fields = []
      if node.get( 'args' ):
        # wrap all string values in double quotes if not already wrapped
        for key in node.get( 'args' ).keys():
          if isinstance(
              node.get( 'args' ).get( key ),
              str ) and node.get( 'args' ).get( key )[ 0 ] != '"' and node.get( 'args' ).get(
                key ) != 'true' and node.get( 'args' ).get( key ) != 'false' and node.get('args').get(key) != 'Debuffs':
            node.get( 'args' )[ key ] = '"' + node.get( 'args' )[ key ] + '"'
          if isinstance( node.get( 'args' ).get( key ), bool ):
            node.get( 'args' )[ key ] = 'true' if node.get( 'args' ).get( 'key' ) else 'false'
        args = [ str( key ) + ': ' + str( value ) for key, value in node.get( 'args' ).items() ]
      if node.get( 'fields' ):
        fields = [ recurse_nodes( child ) for child in node.get( 'fields' ) ]

      alias_str = alias + ': ' if alias else ''
      args_str = '(' + ', '.join( args ) + ')' if args else ''
      fields_str = '{' + ', '.join( fields ) + '}' if fields else ''

      return alias_str + name + args_str + fields_str

    return '{' + recurse_nodes( self.tree ) + '}'

# TODO: Generate this from GraphQL schema

# dict.get method wraps lists in tuples for some reason
def process_fields( fields ):
  if isinstance( fields, tuple ):
    return [ *fields ]
  return [ fields ]

class ReportData( Query ):
  def components( self ):
    return {
      'name': 'reportData',
      'fields': process_fields( self.params.get( 'children' ) )
    }

class Report( Query ):
  parent = ReportData

  def components( self ):
    return {
      'name': 'report',
      'args': {
        'code': self.params.get( 'reportCode' )
      },
      'fields': process_fields( self.params.get( 'children' ) )
    }

class PlayerDetails( Query ):
  parent = Report

  def components( self ):
    return {
      'name': 'playerDetails',
      'args': {
        'translate': False,
        'startTime': self.params.get( 'startTime' ),
        'endTime': self.params.get( 'endTime' )
      }
    }

class MasterData( Query ):
  parent = Report

  def components( self ):
    return {
      'name': 'masterData'
    }

class RateLimitData( Query ):
  def components( self ):
    return {
      'name': 'rateLimitData',
      'fields': process_fields( self.params.get( 'children' ) )
    }

class PointsSpentThisHour( Query ):
  parent = RateLimitData
  cacheable = False

  def components( self ):
    return {
      'name': 'pointsSpentThisHour'
    }

class Fights( Query ):
  parent = Report

  def components( self ):
    return {
      'name':
      'fights',
      'fields': [
        {
          'name': 'id'
        },
        {
          'name': 'encounterID',
        },
        {
          'name': 'name'
        },
        {
          'name': 'difficulty'
        },
        {
          'name': 'kill'
        },
        {
          'name': 'startTime'
        },
        {
          'name': 'endTime'
        },
      ]
    },

class Events( Query ):
  parent = Report

  def components( self ):
    return {
      'name': 'events',
      'args': {
        **self.params.get( 'args' ),
        'startTime': self.params.get( 'startTime' ),
        'endTime': self.params.get( 'endTime' )
      },
      'fields': [ {
        'name': 'data'
      },
                  {
                    'name': 'nextPageTimestamp'
                  } ]
    }
