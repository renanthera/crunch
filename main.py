import wcl
import json
from functools import reduce
from inspect import getmembers

# def type_name_match( l, r ):
#   def attempt( l, r ):
#     if l.lower() == r.lower():
#       return True
#     if l.lower() == r[ 4: ].lower():
#       return True
#     return False

#   # print( l, r, attempt( l, r ), attempt( r, l ) )
#   return attempt( l, r ) or attempt( r, l )

# def find_type_in_types( t ):
#   assert isinstance( t, str ), 't must be a string type token'
#   candidates = [
#     candidate[1]
#     for candidate in getmembers( wcl.types )
#     if type_name_match( candidate[0], t )
#   ] # yapf: disable
#   assert len( candidates ) != 0, f'no type candidates found for {t}'
#   assert len( candidates ) < 2, f'multiple type candidates found for {t}:\n{candidates}'
#   return candidates[ 0 ]

# def eval_type( type_array, *params ):
#   if isinstance( type_array, list ):
#     types = [ find_type_in_types( t ) for t in type_array ]
#     if len( types ) > 1:
#       return reduce( lambda prev, cur: cur( prev ), types[ -2:0 ], types[ -1 ]( *params ) )
#     return types[ 0 ]( *params )

# def base_type( query ):
#   query_root_lower = []
#   if isinstance( query, dict ):
#     query_root_lower = [ key.lower() for key in query.keys() ]
#   if isinstance( query, set ):
#     query_root_lower = [ key.lower() for key in query ]
#   if query_root_lower:
#     # assert len( query_root_lower ) == 1, 'multiple root keys found in query'
#     return {
#       find_type_in_types( t )
#       for t in query_root_lower
#     } # yapf: disable
#   return None

def match_name( l, r ):
  def attempt( l, r ):
    if l.lower() == r.lower():
      return True
    if l.lower() == r[ 4: ].lower():
      return True
    return False

  return attempt( l, r ) or attempt( r, l )

def find_type_from_wcl_types( token ):
  # print(f'TFWT: {token} -> ',end='')
  if not isinstance( token, str ):
    # print(False)
    return False
  candidates = [
    candidate[1]
    for candidate in getmembers( wcl.types )
    if match_name( candidate[0], token )
  ]
  if len( candidates ) == 1:
    # print(candidates[0])
    return candidates[ 0 ]
  # print(False)
  return False

def find_type_from_fields( token, parent ):
  # print(f'TFF: {token} {type(token)} -> ',end='')
  def type_array( token_array ):
    return [
      find_type_from_wcl_types( token )
      for token in token_array
    ]
  if not isinstance( token, str ):
    # print(False)
    return False
  if not isinstance( parent(), wcl.types.GQL_OBJECT ):
    # print(type(parent))
    return False
  # print(parent.fields,end='')
  fields = parent.fields
  candidates = [
    type_array( field[ 'type' ] )
    for field in fields
    if field[ 'name' ].lower() == token.lower()
  ]
  # print('CANDIDATES:', candidates)
  if len( candidates ) == 1:
    return candidates[0]

  return find_type_from_wcl_types( token )

def eval_type_array( type_array, params ):
  def reducer( previous, current ):
    next_obj = current()
    next_obj.update( previous )
    return next_obj

  if not isinstance( type_array, list ):
    return None
  return reduce( reducer, type_array[ -1: 0 ], params )

class Query:
  def __init__( self, query, params ):
    self.query = query
    self.params = params

    self.query_tree = self.create_tree()

  def create_tree( self, query=None, parent=None ):
    # print(f'CT: {query} {parent}')
    if query is None:
      query = self.query
    if isinstance( query, set ):
      return {
        key: k
        for key in query
        if ( k := find_type_from_wcl_types( key ) ) or ( k := find_type_from_fields( key, parent ) )
      }

    if isinstance( query, dict ):
      return {
        k: v
        for key, value in query.items()
        if ( k := find_type_from_wcl_types( key ) ) or ( k := find_type_from_fields( key, parent ) )
        if ( v := find_type_from_wcl_types( value ) ) or ( v := find_type_from_fields( value, k ) ) or ( v := self.create_tree( value, k ) )
      }

    """
    the root node(s) of queries must contain a gql_<name> token
    the child node(s) of queries may contain either gql_<name> tokens or reference
      aliased names found in fields

    args are populated from params dict and arg and param tokens must match

    objects are valid if:
      - all required args are found in params <- this is enforced via GQL_NON_NULL
      - object is found in wcl.types <- this is enforced by find_type_in_types
    """

q = """
alpha: query {
  one: rateLimitData(arg1: 1, arg2: 2) {
    limitperhour pointsspentthishour pointsresetin
  }
}
beta: query {
  two: rateLimitData(arg1: 3, arg2: 4) {
    limitperhour pointsspentthishour pointsresetin
  }
}
gamma: query {
  three: rateLimitData(arg1: 5, arg2: 6) {
    limitperhour pointsspentthishour pointsresetin
  }
}
"""
import re, regex
def process_query( query ):
  """
  alias optional
  token_name required
  args optional but match expected type via introspection
  fields are of the same form as this object
  multiple objects may exist on the same level
  alias?: token_name( arg_k: arg_v... ){ ...fields }
  """
  def process_token_group( query ):
    def any_in( l, r ):
      r = r[ 1:-1 ]
      return any( [
        v in r
        for v in l
      ] )
    def find_tokens_in_token_group( token_group ):
      count = 0
      labels = [ 0 ] + [
        index + 1
        for index, c in enumerate( token_group )
        if c == '{' and ( ( count := count + 1 ) or True ) or True
        if c == '}' and ( ( count := count - 1 ) or True ) or True
        if count == 0 and c in '{}'
      ]
      return [
        token_group[ i:j ]
        for i, j in zip( labels, labels[ 1: ]+[ None ] )
      ][ :-1 ]
    token_group = regex.search( '{((?>[^{}]+|(?R))*)}', query )
    token_group = token_group.group( 1 ) if token_group else ''
    objects = []
    for token in find_tokens_in_token_group( token_group ):
      prefix = re.search( r'^[^{}\(\)]+', token )
      prefix = prefix.group( 0 ) if prefix else ''
      args = re.search( r'\(([^\)]+)\)', token )
      args = args.group( 1 ) if args else ''
      fields = regex.search( '({(?>[^{}]+|(?R))*})', token )
      fields = fields.group( 1 ) if fields else ''
      objects.append( {
        # 'prefix': prefix,
        'alias':  prefix.split( ':' )[ 0 ] if ':' in prefix else '',
        'name':   prefix.split( ':' )[ 1 ] if ':' in prefix else prefix,
        'args':   {
          arg_k: arg_v
          for arg in args.split( ', ' )
          if ( arg_split := arg.split( ':' ) ) and len( arg_split ) > 1
          if ( arg_k := arg_split[ 0 ] ) and ( arg_v := arg_split[ 1 ] )
        },
        'fields': process_token_group( fields ) if any_in( '{}', fields ) else fields[ 1:-1 ].split( ' ' )
      } )
    return objects
  def token_to_object( token ):
    pass
  print(query)
  query = re.sub( r'\s+', ' ', query )
  query = re.sub( r': ', ':', query )
  query = re.sub( r'\s*{\s*', '{', query )
  query = re.sub( r'\s*}\s*', '}', query )
  query = query.strip()
  if query[0] != '{':
    query = '{' + query + '}'
  print(json.dumps(process_token_group(query), indent=2))
process_query(q)
