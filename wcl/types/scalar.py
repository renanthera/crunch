from ..query import GQL_SCALAR

"""
SCALAR TYPES

THIS FILE IS NOT GENERATED
"""

class GQL_Int( GQL_SCALAR ):
  def is_valid( self ):
    return isinstance( self.data, int )

class GQL_String( GQL_SCALAR ):
  def __str__( self ):
    return f'"{self.data}"'

class GQL_Boolean( GQL_SCALAR ):
  def is_valid( self ):
    return isinstance( self.data, bool )

  def __str__( self ):
    return 'true' if self.data else 'false'

class GQL_JSON( GQL_SCALAR ):
  pass

class GQL_Float( GQL_SCALAR ):
  def is_valid( self ):
    return isinstance( self.data, float )

class GQL_ID( GQL_SCALAR ):
  pass
