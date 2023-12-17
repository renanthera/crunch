class Query:
  params = dict()

  parent = None
  cacheable = True
  paginator = {
    'paginationField': None,
    'overrides': None
  }
  args = dict()
  args_override = set()
  fields = []
  children = None

  def components( self ):
    name = self.__class__.__name__
    pagination_field = self.paginator.get( 'paginationField' )
    return {
      'name': name[ 0 ].lower() + name[ 1: ],
      'args': {
        argk: str( argt( self.params.get( argk ) ) ) # pyright: ignore
        for argk, argt in self.args.items()
        if self.params.get( argk ) is not None # pyright: ignore
      } | {
        argo: self.params.get( argo )
        for argo in self.args_override
        if argo is not None
      },
      'fields': [
        field if isinstance( field, dict ) else { 'name': field }
        for field in self.fields + [ self.children, pagination_field ]
        if field is not None
      ]
    } # yapf: disable

  def __init__( self, params, cacheable=None ):
    self.params = params.copy()
    self.children = params.get( 'children' )

    self.tree = self.create_tree()
    self.string = self.stringify()
    self.cacheable = cacheable if cacheable is not None else self.cacheable

  def update( self, params ):
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
        args = [ str( key ) + ': ' + str( value ) for key, value in node.get( 'args' ).items() ]
      if node.get( 'fields' ):
        fields = [ recurse_nodes( child ) for child in node.get( 'fields' ) ]

      alias_str = alias + ': ' if alias else ''
      args_str = '(' + ', '.join( args ) + ')' if args else ''
      fields_str = '{' + ', '.join( fields ) + '}' if fields else ''

      return alias_str + name + args_str + fields_str

    return '{' + recurse_nodes( self.tree ) + '}'

# TODO: Generate this from GraphQL schema

class GraphQLType:
  def __init__( self, value ):
    self.value = value

class GQL_Boolean( GraphQLType ):
  def __str__( self ):
    return str( self.value )

class GQL_String( GraphQLType ):
  def __str__( self ):
    return '"' + str( self.value ) + '"'

class GQL_Int( GraphQLType ):
  def __str__( self ):
    return str( self.value )

class GQL_Float( GraphQLType ):
  def __str__( self ):
    return str( self.value )

class GQL_Enum( GraphQLType ):
  allowed = []

  def __str__( self ):
    assert self.value in self.allowed, f'{self.value} not in {self.__class__.__name__}'
    return self.value

class GQL_EventDataType( GQL_Enum ):
  allowed = [
    'All',
    'Buffs',
    'Casts',
    'CombatantInfo',
    'DamageDone',
    'DamageTaken',
    'Deaths',
    'Debuffs',
    'Dispels',
    'Healing',
    'Interrupts',
    'Resources',
    'Summons',
    'Threat',
  ]

class ReportData( Query ):
  pass

class Report( Query ):
  parent = ReportData
  args = {
    'code': GQL_String
  }

class PlayerDetails( Query ):
  parent = Report
  args = {
    'difficulty': GQL_Int,
    'encounterID': GQL_Int,
    'endTime': GQL_Float,
    # 'fightIDs': GQL_[Int],
    # 'killType': GQL_KillType,
    'startTime': GQL_Float,
    'translate': GQL_Boolean
  }

class MasterData( Query ):
  parent = Report
  args = {
    'translate': GQL_Boolean
  }

class RateLimitData( Query ):
  pass

class PointsSpentThisHour( Query ):
  parent = RateLimitData
  cacheable = False

class Fights( Query ):
  parent = Report
  cacheable = False
  fields = [ 'id', 'encounterID', 'name', 'difficulty', 'kill', 'startTime', 'endTime' ]

class Events( Query ):
  parent = Report
  paginator = {
    'paginationField': 'nextPageTimestamp',
    'overrides': 'startTime'
  }

  args = {
    'abilityID': GQL_Float,
    'dataType': GQL_EventDataType,
    'death': GQL_Int,
    'difficulty': GQL_Int,
    'encounterID': GQL_Int,
    'endTime': GQL_Float,
    # 'fightIDs': [ GQL_Int ],
    'filterExpression': GQL_String,
    # 'hostilityType': GQL_HostilityType,
    'includeResources': GQL_Boolean,
    # 'killType': GQL_KillType,
    'limit': GQL_Int,
    'sourceAurasAbsent': GQL_String,
    'sourceAurasPresent': GQL_String,
    'sourceClass': GQL_String,
    'sourceID': GQL_Int,
    'sourceInstanceID': GQL_Int,
    'startTime': GQL_Float,
    'targetAurasAbsent': GQL_String,
    'targetAurasPresent': GQL_String,
    'targetClass': GQL_String,
    'targetID': GQL_Int,
    'targetInstanceID': GQL_Int,
    'translate': GQL_Boolean,
    'useAbilityIDs': GQL_Boolean,
    'useActorIDs': GQL_Boolean,
    'viewOptions': GQL_Int,
    'wipeCutoff': GQL_Int
  }

  args_override = { 'startTime',
                    'endTime' }

  fields = [ 'data' ]
