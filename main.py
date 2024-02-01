from os import truncate
import analyzers
import wcl

# analyzers.ignited_essence.ignited_essence( [
#   'xrfcz1d34vjJ2LqM',
#   'ygV4kq9RLvGQ2wm8',
#   'vr1RPbDWJ9YakM8j',
# ] )

# analyzers.press_the_advantage.bug_detection( [
#   'xrfcz1d34vjJ2LqM',
#   'CXgx2FPYybAjvn1H',
#   'ny4h6wmpKVbHZq7Q',
#   'gbD8RQrZK7vj1hWF'
# ] )

# analyzers.t31_brew.proc( [
#   'bkrPDQ1ZtTGRphWn',
#   'YftHvBKJzh8nxa9A',
#   'qWJXamNtPbTfZ41y',
#   '7Qct4AXZg8vwrqzL',
#   'ny4h6wmpKVbHZq7Q',
#   'NLMhDBTJw9zq8j2A',
#   'gjvwPqda6KpJ7z3k',
#   'mhbxMrLVFAyDt3Pz',
#   'V2Q4mHvJ8Pg1KTX6',
#   'qFfXM34xTdNaB87V',
#   'XDk2aVCLnyBFKHPr',
# ] )

# analyzers.flaming_germination.flaming_germination(
#   [
#     'AVRh3LdawCzY8HKB'
#   ],
#   [['Lagrimas', 'Katebrew', 'Dandaniel', 'Chizgoblin'],
#   ['Draxxii', 'Diosita', 'Goines', 'Ralfie'],
#   ['Meowge', 'Softmograne', 'Zinglefus', 'Jeefy'],
#   ['Impdh', 'Skovrogue', 'Reddevviil', 'Yusoon'],
#   ['Stragnim', 'Kreemlock', 'Zenvi', 'Harreks']]
# )

# analyzers.flaming_germination.flaming_germination(
#   [
#     'QcW7Z9wajrVRHg8h',
#     'AQhTbnvBy79a62wW',
#     'RjfChnxgt3a8Hypz',
#     'qfvFcyw6LxYHkJ1W',
#     'BmWntKhD6b3VFAkT',
#     'WhnymKat6LrC31fV',
#     'Lk31Aa2KBnTctwWC',
#     'RDkG7VxpC1haP4y3',
#     'kBfxNpzyKDY9nF1w',
#     '2qWtK4JPTbw9BH8d',
#   ],
#   [
#     ['Sinzhu', 'Sussyj', 'Liadryn', 'Jessndecay', 'Olvil', 'Ipsa'],
#     ['Honeymoon', 'Phunt', 'Dragonexarch', 'Remslock', 'Vlces', 'Mystictouch'],
#     ['Learning', 'Eyebrowz', 'Glimmerer', 'Tacofajita', 'Hunkytwunky', 'Bobblywobbly']
#   ]
# )

class GQL_OBJECT:
  name = 'GQL_OBJECT'
  fields = {}

  params = {}
  def __init__( self, ancestry=None ):
    # defer evaluation until runtime so classes are defined
    self.fields = [
      field | {
        'type': eval( field[ 'type' ] ),
        'args': [
          { argk: eval( argv_t ) for argk, argv_t in arg.items() }
          for arg in field[ 'args' ]
        ]
      }
      for field in self.fields
    ]

    if ancestry:
      self.ancestors = [ eval( f'GQL_Object_{ancestry[0]}' )() ]

"""
currently thinking about initializing everything backwards and then i don't need evals
deepest nodes first, then move outward
or some smarter init strategy where you init everything without obj deps
then check if you have resolved any deps for new objs
repeat until objs exhausted

this allows for incomplete initialization of gql objects, as all information
is initialized prior to instantiation of any gql objects

still need a way to ascertain parent in the gql tree, but a path must be provided
to disambaguate requests from each other, or it would be unclear which path to follow
can use that to determine ancestry of objects, thus the correct names for objects and
use the available args
"""

  def init( self, params ):
    def ancestor_list( obj ):
      parent = obj.parent()
      if parent.name != 'GQL_OBJECT':
        yield from ancestor_list( parent )
      yield obj

    self.params = params
    self.ancestors = list( ancestor_list( self ) )
    self.ancestor_names = [ ancestor.name for ancestor in self.ancestors ]
    for ancestor in self.ancestors[:-1]:
      ancestor.init( self.params )

  def str( self, ancestor_names ):
    assert self.params, 'Initialization incomplete'
    args_from_parent = []
    name_from_parent = self.name
    for field in self.parent().fields:
      if isinstance( self, field[ 'type' ] ):
        args_from_parent = field[ 'args' ]
        name_from_parent = field[ 'name' ]
    args = [
      f'{argk}: {argv}'
      for d in args_from_parent
      for argk, argv_t in d.items()
      if ( argv := self.params.get( argk ) )
      if isinstance( argv, argv_t ) or argv_t.is_compatible( argv )
    ]
    fields = [
      f'{argk[ "name" ]}'
      for argk in self.fields
      if argk[ 'name' ] in self.params.keys() and argk[ 'name' ] not in ancestor_names
    ]
    args_str = f'({", ".join(args)})' if args else ''
    fields_str = f'{", ".join(fields)}'
    return name_from_parent, args_str, fields_str

  def __str__( self ):
    string = ''
    for ancestor in reversed( self.ancestors ):
      ancestor_name, ancestor_args_str, ancestor_fields_str = ancestor.str( self.ancestor_names )
      fields_str = ancestor_fields_str + ( ', ' if ancestor_fields_str else '' ) + string
      fields_str = f'{{{fields_str}}}' if ancestor_fields_str or string else fields_str
      string = f'{ancestor_name}{ancestor_args_str}{fields_str}'
    return f'{{{string}}}'

class GQL_Object_Query( GQL_OBJECT ):
  name = 'query'
  fields = [
    {
      'name': 'report',
      'type': 'GQL_Object_Report',
      'args': [
        { 'code': 'GQL_String' },
      ]
    },
  ]

class GQL_Object_Report( GQL_Object_Query, GQL_OBJECT ):
  name = 'report'
  fields = [
    {
      'name': 'code',
      'type': 'GQL_String',
      'args': []
    },
    {
      'name': 'events',
      'type': 'GQL_Object_Events',
      'args': [
        { 'startTime': 'GQL_Int' },
        { 'endTime': 'GQL_Int' },
      ]
    }
  ]

class GQL_Object_Events( GQL_Object_Report, GQL_OBJECT ):
  name = 'events'
  fields = []

class GQL_T:
  compatible_list = []
  value = None
  def __init__( self, value ):
    self.value = value
  @classmethod
  def is_compatible( cls, obj ):
    if type(obj) in cls.compatible_list:
      return True
    return False

class GQL_String( GQL_T ):
  compatible_list = [ str ]
  def __str__( self ):
    return f'"{self.value}"'

class GQL_Int( GQL_T ):
  compatible_list = [ int ]
  def __str__( self ):
    return str(self.value)


def query_lookup( *args ):
  current = eval( f'GQL_Object_{args[0]}()' )
  for arg in args[1:]:
    n = lambda: None
    for field in current.fields:
      if field[ 'name' ] == arg:
        n = field[ 'type' ]
    current = n()
  return current

params = {
  'code': 'asdfjkl',
  'startTime': 100,
  'endTime': 200,
  'report': 'asdf',
  'events': True
}

# print( query_lookup( 'query', 'report', 'events' )( params ) )
# print( query().report().events() )
# print( query().report() )
q = query_lookup( 'Query', 'report', 'events' )
q.init( params )
print( q )

# print( query_lookup( 'query', 'report', 'events' )() )
# print( query_lookup( 'query', 'report' )() )
# print( query_lookup( 'query' )() )

import unicodedata
from keyword import iskeyword
import random
import sys

def is_allowed_unicode_char( c, position ):
  # Other_ID_Start and Other_ID_Continue are from the following webpage with the matching category (?) name
  # https://www.unicode.org/Public/15.0.0/ucd/PropList.txt
  Other_ID_Start = { '\u1885', '\u1886', '\u2118', '\u212E', '\u309B', '\u309C' }
  Other_ID_Continue = { '\u00B7', '\u0387', '\u1369', '\u1370', '\u1371', '\u19DA' }
  # id_start and id_continue category_codes are defined from the following webpage:
  # https://docs.python.org/3/reference/lexical_analysis.html#identifiers
  id_start_category_codes = { 'Lu', 'Ll', 'Lt', 'Lm', 'Lo', 'Nl' }
  id_continue_category_codes = id_start_category_codes | { 'Mn', 'Mc', 'Nd', 'Pc' }
  # id_start and id_continue singletons are defined from the following webpage:
  # https://docs.python.org/3/reference/lexical_analysis.html#identifiers
  id_start_singletons = { '_' } | Other_ID_Start
  id_continue_singletons = id_start_singletons | Other_ID_Continue

  if unicodedata.category( c ) in id_start_category_codes or c in id_start_singletons:
    return c
  if position > 0 and ( unicodedata.category( c ) in id_continue_category_codes or c in id_continue_singletons ):
    return c

def generate_unicode_identifier( length = 16 ):
  # This implementation is correct, but returned strings are:
  # - Unmanageably unreadable
  # - Not reliably generated due to too small of a character set (to improve readability)
  # - Requires too much pregeneration (to avoid unreliable generation)

  # This does not generate all possible unicode identifiers, as I did not find
  # a way to find all characters that NFKC normalize to a valid character.
  def generate_chr(attempt = 0):
    c = chr( random.randrange( sys.maxunicode + 1 ) )
    if is_allowed_unicode_char( c, 0 ):
      return c
    return generate_chr( attempt + 1 )

  candidate_str = ''.join( [
    c
    for _ in range( length )
    if ( c := generate_chr() )
  ] )

  if not iskeyword( candidate_str ):
    return candidate_str
  return generate_unicode_identifier( length = length )

def generate_ascii_identifier( length = 16 ):
  # Only a small subset of valid Python 3 Identifiers, but:
  # - Highly readable
  # - Still millions of combinations
  # - More trivial to generate
  MIN_ASCII = 33
  MAX_ASCII = 126

  def generate_chr( position, attempts = 0 ):
    character = chr( random.randrange( MIN_ASCII, MAX_ASCII ) )
    if is_allowed_unicode_char( character, position ):
      return character
    return generate_chr( position, attempts + 1)

  candidate_str = '_' + ''.join( [
    generate_chr( pos )
    for pos in range( length - 1 )
  ] )

  if not iskeyword( candidate_str ) and candidate_str.isidentifier():
    return candidate_str
  return generate_ascii_identifier( length = length )


# for k in range( 5 ):
#   ident = generate_ascii_identifier()
#   print(ident, len(ident))



# PROBLEM:
# - nested classes are gross
# - having no nested classes with their actual names results in namespace clashes
# SOLUTION:
# a)
#   - queries with no parents get their actual name for their object name
#   - queries with parents get an internal name, and are added to the parent with their real name via `__subclasses__()` and `setattr(...)`
# b)
#   - infrastructure exists for type hoisting, but it may not be useful in this situation

# print(C())
# print(C().D())

# print( A() )
# for q in A().children:
#   print( q(), q().parent() )
#   for u in q().children:
#     print( u(), u().parent() )
