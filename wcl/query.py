class Query:
  params = {}
  parent = None
  cacheable = True
  paginator = {
    'paginationField': None,
    'overrides': None
  }
  args = {}
  fields = []
  children = None

  def components( self ):
    name = self.__class__.__name__
    pagination_field = self.paginator.get( 'paginationField' )
    return {
      'name': name[ 0 ].lower() + name[ 1: ],
      'args': {
        argk: GQL_type_handler( argt, self.params.get( argk ) )
        for argk, argt in self.args.items()
        if self.params.get( argk ) is not None
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

def GQL_type_handler( argt, value ):
  if isinstance( argt, list ):
    return GQL_List( value, argt[ 0 ] )
  return argt( value )

class GraphQLType:
  def __init__( self, value ):
    self.value = value

class GQL_Boolean( GraphQLType ):
  def __str__( self ):
    return str( self.value and 'true' or 'false' )

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
    assert self.value in self.allowed, f'{self.value} not in Enum {self.__class__.__name__}'
    return self.value

class GQL_List( GraphQLType ):
  def __init__( self, value, secondaryType ):
    super().__init__( value )
    self.secondaryType = secondaryType

  def __str__( self ):
    assert self.secondaryType is not None, 'Secondary type is not defined for list object'
    assert isinstance( self.value, list ), 'Values are not a list'
    return '[' + ', '.join( [ str( self.secondaryType( val ) ) for val in self.value ] ) + ']'

# TODO: Generate this from GraphQL schema

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

class GQL_RankingCompareType( GQL_Enum ):
  allowed = [
    'Rankings',
    'Parses'
  ]

class GQL_CharacterRankingMetricType( GQL_Enum ):
  allowed = [
    'bossdps',
    'default',
    'dps',
    'hps',
    'krsi',
    'playerscore',
    'playerspeed',
    'tankhps',
    'wdps',
    'bosscdps',               # FFXIV
    'cdps',                   # FFXIV
    'ndps',                   # FFXIV
    'rdps',                   # FFXIV
    'bossndps',               # FFXIV
    'bossrdps',               # FFXIV
    'healercombineddps',      # FFXIV
    'healercombinedbossdps',  # FFXIV
    'healercombinedcdps',     # FFXIV
    'healercombinedbosscdps', # FFXIV
    'healercombinedndps',     # FFXIV
    'healercombinedbossndps', # FFXIV
    'healercombinedrdps',     # FFXIV
    'healercombinedbossrdps', # FFXIV
    'tankcombineddps',        # FFXIV
    'tankcombinedbossdps',    # FFXIV
    'tankcombinedcdps',       # FFXIV
    'tankcombinedbosscdps',   # FFXIV
    'tankcombinedndps',       # FFXIV
    'tankcombinedbossndps',   # FFXIV
    'tankcombinedrdps',       # FFXIV
    'tankcombinedbossrdps',   # FFXIV
  ]

class GQL_RoleType( GQL_Enum ):
  allowed = [
    'Any',
    'DPS',
    'Healer',
    'Tank',
  ]

class GQL_RankingTimeframeType( GQL_Enum ):
  allowed = [
    'Today',
    'Historical'
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
    'fightIDs': [ GQL_Int ],
    # 'killType': GQL_KillType,
    'startTime': GQL_Float,
    'translate': GQL_Boolean
  }

class MasterData( Query ):
  parent = Report
  args = {
    'translate': GQL_Boolean
  }

class Actors( Query ):
  parent = MasterData
  args = {
    'type': GQL_String,
    'subType': GQL_String
  }

  fields = [ 'gameID', 'icon', 'id', 'name', 'petOwner', 'server', 'subType', 'type' ]

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
    'fightIDs': [ GQL_Int ],
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

  fields = [ 'data' ]

class CharacterData( Query ):
  pass

class Character( Query ):
  parent = CharacterData
  args = {
    'id': GQL_Int,
    'name': GQL_String,
    'serverSlug': GQL_String,
    'serverRegion': GQL_String
  }

class EncounterRankings( Query ):
  parent = Character
  args = {
    'byBracket': GQL_Boolean,
    'className': GQL_String,
    'compare': GQL_RankingCompareType,
    'difficulty': GQL_Int,
    'encounterID': GQL_Int,
    'includeCombatantInfo': GQL_Boolean,
    'includeOtherPlayers': GQL_Boolean,
    'includeHistoricalGraph': GQL_Boolean,
    'includePrivateLogs': GQL_Boolean,
    'metric': GQL_CharacterRankingMetricType,
    'partition': GQL_Int,
    'role': GQL_RoleType,
    'size': GQL_Int,
    'specName': GQL_String,
    'timeframe': GQL_RankingTimeframeType
  }
