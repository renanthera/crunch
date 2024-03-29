from .primitives import GQL_SCALAR

"""
SCALAR TYPES

THIS FILE IS NOT GENERATED
"""

class GQL_Int( GQL_SCALAR ):
  base_type = int

class GQL_String( GQL_SCALAR ):
  base_type = str

  def __str__( self ):
    self.is_valid()
    return f'"{self.data}"'

class GQL_Boolean( GQL_SCALAR ):
  base_type = bool

  def __str__( self ):
    self.is_valid()
    return 'true' if self.data else 'false'

class GQL_Float( GQL_SCALAR ):
  base_type = float

class GQL_JSON( GQL_SCALAR ):
  pass

class GQL_ID( GQL_SCALAR ):
  pass
