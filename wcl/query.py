# class Query:
#     prefix = ''
#     kind = ''
#     suffix = ''

#     def __init__(self, args, fields):
#         self.args = args
#         self.fields = fields
#         self.query = self.stringify()

#     def stringify(self):
#         if (self.args is None):
#             query = self.prefix + self.kind
#         else:
#             query = self.prefix + self.kind + '('

#         if isinstance(self.args, str):
#             query += self.args + ' '
#         elif isinstance(self.args, dict):
#             for key, value in self.args.items():
#                 if value is not None:
#                     query += key + ':' + str(value) + ' '
#         elif isinstance(self.args, set):
#             for value in self.args.items():
#                 query += value + ' '

#         if (self.args is None):
#             query = query + '{'
#         else:
#             query = query[:-1] + '){'

#         if isinstance(self.fields, str):
#             query += self.fields + ' '
#         elif isinstance(self.fields, dict):
#             for key, value in self.fields.items():
#                 if value is not None:
#                     query += key + ':' + str(value) + ' '
#         elif isinstance(self.fields, set):
#             for value in self.fields:
#                 query += value + ' '
#         query = query[:-1] + '}' + self.suffix

#         return query

#     def update_query(self, args=None, fields=None):
#         if args is not None:
#             for key, value in args.items():
#                 self.args.update({key: value})
#         if fields is not None:
#             for key, value in fields.items():
#                 self.fields.update({key: value})
#         self.query = self.stringify()
def parent_components( Parent, *args ):
  return Parent( *args ).components

class GraphQLObject:
  def __init__(self, *params):
    self.params = params
    self.components = {}
    self.complete = False
    self.cache = False

class ReportData(GraphQLObject):
  def __init__( self, children ):
    super().__init__(children)
    self.components = {
      'name': 'reportData',
      'fields': [ children ]
    }

class Report:
  def __init__( self, children, reportCode ):
    self.components = parent_components(
      ReportData,
      {
        'name': 'report',
        'args': {
          'code': reportCode
        },
        'fields': [ children ]
      }
    )

class PlayerDetails:
  def __init__( self, reportCode, startTime, endTime ):
    self.components = parent_components(
      Report,
      {
        'name': 'playerDetails',
        'args': {
          'translate': 'false',
          'startTime': startTime,
          'endTime': endTime
        }
      },
      reportCode
    )

class MasterData:
  def __init__( self, reportCode ):
    self.components = parent_components(
      Report,
      {
        'name': 'masterData'
      },
      reportCode
    ) # yapf: disable

class RateLimitData:
  def __init__( self, children ):
    self.components = {
      'name': 'rateLimitData',
      'fields': [ children ]
    }

class PointsSpentThisHour:
  def __init__( self ):
    self.components = parent_components(
      RateLimitData,
      {
        'name': 'pointsSpentThisHour'
      }
    ) # yapf: disable

class Fights:
  def __init__( self, reportCode ):
    self.components = parent_components(
      Report,
      {
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
      reportCode
    )

class Events:
  def __init__( self, reportCode, args ):
    self.components = parent_components(
      Report,
      {
        'name': 'events',
        'args': args,
        'fields': [ {
          'name': 'data'
        },
                    {
                      'name': 'nextPageTimestamp'
                    } ]
      },
      reportCode
    )

import json
import functools

class Query:
  # TODO: MERGE QUERIES USING GENERATED ALIASES
  # TODO: UPDATE QUERIES TO FULLY PAGINATE RESULT
  # TODO: REWORK REQUEST
  def __init__( self ):
    self.query_trees = []
    self.query_strings = []

  def add_tree( self, query_tree ):
    self.query_trees.append( query_tree )

  def merge_trees( self ):
    # find if any queries of the same type with different parameters exists
    self.query_tree = {}
    for tree in self.query_trees:
      print( tree.components )
      mergeable_count = functools.reduce(
        lambda a, b: a + b, # yapfify: disable
        [ type( tree ) is type( t ) and tree != t for t in self.query_trees ]
      )
      print( mergeable_count )

  def stringify_trees( self ):
    def recurse_tree( current ):
      name = current.get( 'name' )
      alias = current.get( 'alias' )
      args = []
      if current.get( 'args' ):
        args = [ str( k ) + ': ' + str( v ) for k, v in current.get( 'args' ).items() ]
      children = []
      if current.get( 'fields' ):
        children = [ recurse_tree( tree ) for tree in current.get( 'fields' ) ]

      alias_str = ''
      if alias:
        alias_str = alias + ': '
      args_str = ''
      if args:
        args_str = '(' + ', '.join( args ) + ')'
      children_str = ''
      if children:
        children_str = '{' + ', '.join( children ) + '}'

      return alias_str + name + args_str + children_str

    print( 'stringifying...' )
    self.query_strings = []
    for tree in self.query_trees:
      query = '{' + recurse_tree( tree.components ) + '}'
      self.query_strings.append( query )
      print( query )
      print( json.dumps( tree.components, indent=2 ) )
