# from copy import deepcopy

# class Query:
#   # params
#   query_params = {}
#   cacheable = True

#   # internal objects
#   args = {}
#   children = None
#   fields = []
#   name = None
#   parent = None
#   paginator = {
#     'paginationField': None,
#     'overrides': None,
#     'callback': None
#   }

#   def components( self ):
#     pagination_field = self.paginator.get( 'paginationField' )
#     return {
#       'name': self.name,
#       'args': {
#         argk: GQL_Type_Handler( argt, self.query_params.get( argk ) )
#         for argk, argt in self.args.items()
#         if self.query_params.get( argk ) is not None
#       },
#       'fields': [
#         field if isinstance( field, dict ) else { 'name': field }
#         for field in self.fields + [ self.children, pagination_field ]
#         if field is not None
#       ]
#     } # yapf: disable

#   def __init__( self, query_params, cacheable=None ):
#     self.query_params = deepcopy( query_params )

#     self.children = self.query_params.get( 'children' )
#     self.tree = self.create_tree()
#     self.string = self.stringify()
#     self.cacheable = cacheable if cacheable is not None else self.cacheable

#   def update( self, params ):
#     assert all( [
#       type( self.query_params.get( key ) ) is type( params.get( key ) ) or params.get( key ) is None
#       for key in self.query_params
#     ] ), 'Types of values do not match'
#     assert params != self.query_params, 'Params are unchanged'

#     self.query_params.update( params )
#     self.tree = self.create_tree()

#   def create_tree( self ):
#     self.query_params.update( {
#       'children': self.components()
#     } )

#     if self.parent is None:
#       return self.query_params.get( 'children' )
#     return self.parent( self.query_params ).tree

#   def stringify( self ):
#     def recurse_nodes( node ):
#       alias = node.get( 'alias' )
#       name = node.get( 'name' )
#       args = []
#       fields = []
#       if node.get( 'args' ):
#         args = [ str( key ) + ': ' + str( value ) for key, value in node.get( 'args' ).items() ]
#       if node.get( 'fields' ):
#         fields = [ recurse_nodes( child ) for child in node.get( 'fields' ) ]

#       alias_str = alias + ': ' if alias else ''
#       args_str = '(' + ', '.join( args ) + ')' if args else ''
#       fields_str = '{' + ', '.join( fields ) + '}' if fields else ''

#       return alias_str + name + args_str + fields_str

#     return '{' + recurse_nodes( self.tree ) + '}'

# def GQL_Type_Handler( argt, value ):
#   if isinstance( argt, list ):
#     return GQL_List( value, argt[ 0 ] )
#   return argt( value )

# class GQL_Type:
#   def __init__( self, value ):
#     self.value = value

# class GQL_Boolean( GQL_Type ):
#   def __str__( self ):
#     return str( self.value and 'true' or 'false' )

# class GQL_String( GQL_Type ):
#   def __str__( self ):
#     return '"' + str( self.value ) + '"'

# class GQL_Int( GQL_Type ):
#   def __str__( self ):
#     return str( self.value )

# class GQL_Float( GQL_Type ):
#   def __str__( self ):
#     return str( self.value )

# class GQL_Enum( GQL_Type ):
#   allowed = []

#   def __str__( self ):
#     assert self.value in self.allowed, f'{self.value} not in Enum {self.__class__.__name__}'
#     return self.value

# class GQL_List( GQL_Type ):
#   def __init__( self, value, secondaryType ):
#     super().__init__( value )
#     self.secondaryType = secondaryType

#   def __str__( self ):
#     assert self.secondaryType is not None, 'Secondary type is not defined for list object'
#     assert isinstance( self.value, list ), 'Values are not a list'
#     return '[' + ', '.join( [ str( self.secondaryType( val ) ) for val in self.value ] ) + ']'

# # TODO: Generate this from GraphQL schema

# class GQL_EventDataType( GQL_Enum ):
#   allowed = [
#     'All',
#     'Buffs',
#     'Casts',
#     'CombatantInfo',
#     'DamageDone',
#     'DamageTaken',
#     'Deaths',
#     'Debuffs',
#     'Dispels',
#     'Healing',
#     'Interrupts',
#     'Resources',
#     'Summons',
#     'Threat',
#   ]

# class ReportData( Query ):
#   pass

# class Report( Query ):
#   parent = ReportData
#   args = {
#     'code': GQL_String
#   }

# class PlayerDetails( Query ):
#   parent = Report
#   args = {
#     'difficulty': GQL_Int,
#     'encounterID': GQL_Int,
#     'endTime': GQL_Float,
#     'fightIDs': [ GQL_Int ],
#     # 'killType': GQL_KillType,
#     'startTime': GQL_Float,
#     'translate': GQL_Boolean
#   }

# class MasterData( Query ):
#   parent = Report
#   args = {
#     'translate': GQL_Boolean
#   }

# class Actors( Query ):
#   parent = MasterData
#   args = {
#     'type': GQL_String,
#     'subType': GQL_String
#   }

#   fields = [ 'gameID', 'icon', 'id', 'name', 'petOwner', 'server', 'subType', 'type' ]

# class RateLimitData( Query ):
#   pass

# class PointsSpentThisHour( Query ):
#   parent = RateLimitData
#   cacheable = False

# class Fights( Query ):
#   parent = Report
#   cacheable = False
#   fields = [ 'id', 'encounterID', 'name', 'difficulty', 'kill', 'startTime', 'endTime' ]

# class Events( Query ):
#   parent = Report
#   paginator = {
#     'paginationField': 'nextPageTimestamp',
#     'overrides': 'startTime'
#   }

#   args = {
#     'abilityID': GQL_Float,
#     'dataType': GQL_EventDataType,
#     'death': GQL_Int,
#     'difficulty': GQL_Int,
#     'encounterID': GQL_Int,
#     'endTime': GQL_Float,
#     'fightIDs': [ GQL_Int ],
#     'filterExpression': GQL_String,
#     # 'hostilityType': GQL_HostilityType,
#     'includeResources': GQL_Boolean,
#     # 'killType': GQL_KillType,
#     'limit': GQL_Int,
#     'sourceAurasAbsent': GQL_String,
#     'sourceAurasPresent': GQL_String,
#     'sourceClass': GQL_String,
#     'sourceID': GQL_Int,
#     'sourceInstanceID': GQL_Int,
#     'startTime': GQL_Float,
#     'targetAurasAbsent': GQL_String,
#     'targetAurasPresent': GQL_String,
#     'targetClass': GQL_String,
#     'targetID': GQL_Int,
#     'targetInstanceID': GQL_Int,
#     'translate': GQL_Boolean,
#     'useAbilityIDs': GQL_Boolean,
#     'useActorIDs': GQL_Boolean,
#     'viewOptions': GQL_Int,
#     'wipeCutoff': GQL_Int
#   }

#   fields = [ 'data' ]

# class Reports( Query ):
#   parent = ReportData
#   paginator = {
#     'paginationField': 'current_page',
#     'overrides': 'page'
#   }

#   args = {
#     'endTime': GQL_Float,
#     'guildID': GQL_Int,
#     'guildName': GQL_String,
#     'guildServerSlug': GQL_String,
#     'guildServerRegion': GQL_String,
#     'guildTagID': GQL_Int,
#     'userID': GQL_Int,
#     'limit': GQL_Int,
#     'page': GQL_Int,
#     'startTime': GQL_Float,
#     'zoneID': GQL_Int,
#     'gameZoneID': GQL_Int
#   }

#   fields = [
#     'data',
#     'total',
#     'per_page',
#     'current_page',
#     'from',
#     'to',
#     'last_page',
#     'has_more_pages'
#   ]

# # GQL 2.0
# # object_name( {argument_key: argument_value, ...} ){ [field, ...] }

# class GQL_OBJECT:
#   # Provided by instantiator
#   alias = None
#   args = {}
#   fields = {}

#   # Provided by code generation
#   arg_types = {}
#   field_types = {}
#   name = None
#   parent = None
#   paginator = {
#     'field': None,
#     'replaces': None,
#     'callback': None
#   }

#   def __init__( self, args, fields ):
#     # Update name of child in fields and in the child object
#     # children may have multiple parents, and be called different things by each
#     if fields.get( 'child' ) is not None:
#       expected_name = None
#       child = fields[ 'child' ]
#       for name, t in self.field_types.items():
#         if isinstance( child, t ):
#           expected_name = name
#           break
#       if expected_name is not None:
#         fields.update( {
#           expected_name: child
#         } )
#         fields[ expected_name ].name = expected_name
#         fields.pop( 'child' )

#     # Verify all arguments and fields are of the expected types
#     assert all( [
#       isinstance( arg_v, expected_type )
#       for arg_k, arg_v in args.items()
#       if ( expected_type := self.arg_types.get( arg_k ) )
#     ] ), f'Not all args are for {self.__class__.__name__} ({self.name}) are of the expected type.\n{args}\n{self.arg_types}'
#     assert all( [
#       isinstance( field_v, expected_type )
#       for field_k, field_v in fields.items()
#       if ( expected_type := self.field_types.get( field_k ) )
#     ] ), f'Not all fields are for {self.__class__.__name__} ({self.name}) are of the expected type.\n{fields}\n{self.field_types}'

#     self.args = args
#     self.fields = fields

#   def __str__( self ):
#     args = [
#       f'{key}: {str( value )}'
#       for key, value in self.args.items()
#       if hasattr( value, '__str__' ) and key in self.arg_types.keys()
#     ] # yapf: disable
#     fields = [
#       f'{str( value )}'
#       for key, value in self.fields.items()
#       if hasattr( value, '__str__' ) and key in self.field_types.keys()
#     ] # yapf: disable
#     args_str = ( '(' if len( args ) > 0 else
#                  '' ) + ','.join( args ) + ( ')' if len( args ) > 0 else '' )
#     fields_str = ( '{' if len( fields ) > 0 else
#                    '' ) + ','.join( fields ) + ( '}' if len( fields ) > 0 else '' )
#     alias_str = self.alias + ': ' if self.alias is not None else ''
#     return f'{alias_str}{self.name}{args_str}{fields_str}'

#   def tree( self ):
#     if self.parent is not None:
#       # print( f'creating {self.parent.__name__} with:\nargs: {self.args}\nfields: {self.fields | { "child": self }}')
#       return self.parent( self.args,
#                           self.fields | {
#                             'child': self
#                           } ).tree()
#     return self

# class GQL_SCALAR:
#   def __init__( self, value ):
#     self.value = value

#   def __str__( self ):
#     return f'{self.value}'

# class GQL_SCALAR_Boolean( GQL_SCALAR ):
#   def __str__( self ):
#     return f'{self.value and "true" or "false"}'

# class GQL_SCALAR_Float( GQL_SCALAR ):
#   pass

# class GQL_SCALAR_Int( GQL_SCALAR ):
#   pass

# class GQL_SCALAR_String( GQL_SCALAR ):
#   def __str__( self ):
#     return f'"{self.value}"'

# class GQL_ENUM:
#   allowed = []

#   def __init__( self, value ):
#     self.value = value

#   def __str__( self ):
#     assert self.value in self.allowed, f'{self.value} is not in Enum {self.__class__.__name__}.'
#     return f'{self.value}'

# # class GQL_OBJECT_<NAME>( GQL_Object ):
# #   def __init__( self, args, fields ):
# #     self.arg_types = {
# #       <ARG_NAME>: GQL_<ARG_TYPE_NAME>,
# #       ...
# #     }
# #     self.field_types = {
# #       <FIELD_NAME>: GQL_<FIELD_TYPE_NAME>,
# #       ...
# #     }
# #     self.name = <NAME_FIELD>
# #     self.parent = GQL_<PARENT_TYPE_NAME>
# #     self.paginator = {
# #       'field': <FIELD_NAME>,
# #       'replaces': <ARG_NAME>,
# #       'callback': <lambda FIELD_VALUE: ARG_VALUE>
# #     }
# #     super().__init__( args, fields )
# class GQL_Test1( GQL_OBJECT ):
#   def __init__( self, args, fields ):
#     self.name = 'test-one'
#     self.field_types = {
#       'newname-two': GQL_Test2
#     }
#     super().__init__( args, fields )

# class GQL_Test2( GQL_OBJECT ):
#   def __init__( self, args, fields ):
#     self.name = 'test-two'
#     self.parent = GQL_Test1
#     super().__init__( args, fields )

"""
1. each object uses the canonical GQL typename as its name
2. each object contains two sets of references: args and fields
2. each reference contains GQL typename, local aliased name and metadata
"""
"""
BASE KINDS:
SCALAR,
OBJECT,
ENUM

META KINDS:
NON_NULL,
LIST
"""
"""
META TYPE KINDS
"""

class GQL_KIND:
  def __init__( self, data ):
    self.data = data
    assert self.is_valid()

  def __str__( self ):
    return str( self.data )

  def is_valid( self ):
    return False

class GQL_SCALAR( GQL_KIND ):
  def is_valid( self ):
    return True

class GQL_ENUM( GQL_KIND ):
  enum_values = []

  def is_valid( self ):
    return self.data in self.enum_values

class GQL_NON_NULL( GQL_KIND ):
  def is_valid( self ):
    return isinstance( self.data, GQL_KIND ) and self.data.is_valid()

class GQL_LIST( GQL_KIND ):
  def __str__( self ):
    return '[' + ', '.join( [ str( datum ) for datum in self.data ] ) + ']'

  def is_valid( self ):
    return isinstance( self.data, list ) and all( [ hasattr( datum, 'is_valid' ) and datum.is_valid() for datum in self.data ] ) # yapf: disable

if __name__ == '__main__':
  import json
  from request import Request

  class SchemaIntrospection:
    schema_location = 'wcl/introspection_query.json'
    tree = {
      'name': '__schema'
    }
    paginator = {}
    cacheable = True

    def __str__( self ):
      with open( self.schema_location, 'r' ) as handle:
        data = handle.read()
      return data

  schema_query = SchemaIntrospection()
  schema_request_data = Request( schema_query ).data

  tab = '  '
  objects = {
    'ENUM': [
"""from query import GQL_ENUM

\"\"\"
ENUM TYPES
THIS FILE IS GENERATED BY `wcl/query.py`.
\"\"\""""
    ],
    'OBJECT': [
"""from query import GQL_Object
import enum
import scalar

\"\"\"
OBJECT TYPES
THIS FILE IS GENERATED BY `wcl/query.py`.
\"\"\""""
    ]
  }

  def handle_enum( entry ):
    assert entry[ 'kind' ] == 'ENUM'
    longest_str = max( [ len( enum_value[ 'name' ] ) for enum_value in entry[ 'enumValues' ] ] )
    lines = [
      f'class GQL_{entry["name"]}( GQL_ENUM ):',
      f'{tab}enum_values = [',
      *[
        f'{tab*2}\'{name}\',{" "*(longest_str-len(name))} # {desc}'
        for enum_value in entry['enumValues']
        if ( name := enum_value['name'] )
        if ( desc := enum_value['description'] )
      ],
      f'{tab}]'
    ] # yapf: disable
    return '\n'.join( lines )

  def handle_object( entry ):
    return ""

  for k in schema_request_data[ 'types' ]:
    kind = k[ 'kind' ]
    if kind in objects.keys():
      current = objects[ kind ]
      match kind:
        case 'ENUM':
          current.append( handle_enum( k ) )
        case 'OBJECT':
          current.append( handle_object( k ) )
        case _:
          pass

      objects.update( {
        kind: current
      } )
  for kind, values in objects.items():
    with open( f'wcl/types/{kind.lower()}.py', 'w' ) as handle:
      handle.write( '\n\n'.join( values ) )
