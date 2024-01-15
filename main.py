# def tier_guard_analysis( info ):
#   reportCode = info.get( 'reportCode' )
#   startTime = info.get( 'startTime' )
#   endTime = info.get( 'endTime' )
#   id = info.get( 'id' )
#   charred_dreams = wcl.getEvents(
#     reportCode,
#     None,
#     {
#       'dataType': 'DamageDone',
#       'abilityID': 425299,
#       'startTime': startTime,
#       'endTime': endTime,
#       'useAbilityIDs': 'true',
#       'sourceID': id
#     }
#   )
#   shadowflame_wreathe = wcl.getEvents(
#     reportCode,
#     None,
#     {
#       'dataType': 'DamageDone',
#       'abilityID': 406764,
#       'startTime': startTime,
#       'endTime': endTime,
#       'useAbilityIDs': 'true',
#       'sourceID': id
#     }
#   )
#   celestial_brew = wcl.getEvents(
#     reportCode,
#     None,
#     {
#       'dataType': 'Buffs',
#       'abilityID': 425965,
#       'startTime': startTime,
#       'endTime': endTime,
#       'useAbilityIDs': 'true',
#       'sourceID': id
#     }
#   )
#   charred_dreams_data = list( chain.from_iterable( charred_dreams.data ) )
#   shadowflame_wreathe_data = list( chain.from_iterable( shadowflame_wreathe.data ) )
#   celestial_brew_data = list( chain.from_iterable( celestial_brew.data ) )

#   # flatten data
#   # healing_data      = list(chain.from_iterable(healing.data))
#   # buffs_data        = list(chain.from_iterable(buffs.data))
#   # casts_data        = list(chain.from_iterable(casts.data))
#   # damage_taken_data = list(chain.from_iterable(damage_taken.data))

#   # merge data and sort by timestamp
#   data = sorted(
#       # healing_data + buffs_data + casts_data + damage_taken_data,
#       # healing_data,
#       charred_dreams_data + celestial_brew_data + shadowflame_wreathe_data, # + elementium_pocket_anvil_data,
#       key=lambda s: (s.get('timestamp')))

#   acc = 0
#   amt = 0
#   ct = 0
#   for k in data:
#     spell_id = k.get( 'abilityGameID' )
#     if spell_id == 425299:
#       amt += k.get( 'unmitigatedAmount' )
#       # print(k.get('sourceID'), k.get('targetID'))
#       # amt += k.get('amount')
#     # if spell_id == 425965 and k.get('type') == 'removebuff':
#     #     print(k)
#     #     amt = 0
#     if spell_id == 425965 and k.get( 'type' ) == 'applybuff':
#       absorb = k.get( 'absorb' )
#       reverse_crit_vers = absorb / ( 1 + 0.8 * 0.4007 ) / ( 1 + 0.2165 )
#       acc += absorb
#       ct += 1
#       # print('Absorb:', k.get('absorb'))
#       # print('Damage Dealt since last:', amt)
#       # print('Difference:', amt - absorb)
#       # print('Reverse crit and vers:', reverse_crit_vers)
#       # if amt > 0:
#       # print('Ratio:', absorb / amt)
#       # print('Inverse ratio:', amt / absorb)
#       # print('Reverse Ratio:', reverse_crit_vers / amt)
#       # print()
#       amt = 0

#   print( acc / ct )

# # runReports(tier_proc_analysis)
# # runReports(tier_guard_analysis)

# # wcl.Request(wcl.PointsSpent())
# # wcl.getPointsSpent()

# import json

import analyzers

# analyzers.ignited_essence.ignited_essence( [
#   'xrfcz1d34vjJ2LqM',
#   'ygV4kq9RLvGQ2wm8',
#   'vr1RPbDWJ9YakM8j',
# ] )

analyzers.press_the_advantage.bug_detection( [
  'xrfcz1d34vjJ2LqM',
  'CXgx2FPYybAjvn1H',
  'ny4h6wmpKVbHZq7Q',
  'gbD8RQrZK7vj1hWF'
] )

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

import wcl

# t = wcl.GQL_Object( {'asdf': 'fdsa'}, {'jkl': 'lkj'} )
# print(t)

# class Test:
#   asdf = 'jkl'

# d = {
#   '1': Test
# }

# for v in d.values():
#   print(isinstance(Test(), v))

# u = wcl.GQL_Test1( {}, {} ).tree()
# v = wcl.GQL_Test2( {}, {} ).tree()
# print(u)
# print(v)
class GQL_OBJECT:
  active = []
  name = 'GQL_OBJECT'
  def __init__( self, child_class_name = '', child_str = '' ):
    self.child_class_name = child_class_name
    self.child_str = child_str

    self.parent = self.__class__.__mro__[1]
    self.children = list(self.__class__.__subclasses__())

  def __str__( self ):
    children = [
      self.child_str if child.name == self.child_class_name else str( child.name )
      for child in self.children
      if child.name in self.active
    ]
    ret = self.name
    if len( children ):
      ret += '{' + ', '.join( children ) + '}'
    if self.parent.__name__ != 'GQL_OBJECT':
      return str( self.parent( self.name, ret ) )
    return '{' + ret + '}'

class query( GQL_OBJECT ):
  name = 'query'
  active = [ 'report' ]
  report = lambda *args, **kwargs: eval( '_QrsNKiY_WLpJ6Iu_report' )( *args, **kwargs )

class _QrsNKiY_WLpJ6Iu_report( query, GQL_OBJECT ):
  name = 'report'
  active = [ 'code', 'events' ]
  code = lambda *args, **kwargs: eval( '_MqAkvZzWS6CGIGj_code' )( *args, **kwargs )
  events = lambda *args, **kwargs: eval( '_GZ3efcSVmPvraRn_events' )( *args, **kwargs )

class _MqAkvZzWS6CGIGj_code( _QrsNKiY_WLpJ6Iu_report, GQL_OBJECT ):
  name = 'code'

class _GZ3efcSVmPvraRn_events( _QrsNKiY_WLpJ6Iu_report, GQL_OBJECT ):
  name = 'events'

print( query().report().events() )

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
