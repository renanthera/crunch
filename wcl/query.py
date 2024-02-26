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

class GQL_OBJECT( GQL_KIND ):
  pass

class GQL_NON_NULL( GQL_KIND ):
  def is_valid( self ):
    return isinstance( self.data, GQL_KIND ) and self.data.is_valid()

class GQL_LIST( GQL_KIND ):
  def __str__( self ):
    return '[' + ', '.join( [ str( datum ) for datum in self.data ] ) + ']'

  def is_valid( self ):
    return isinstance( self.data, list ) and all( [ hasattr( datum, 'is_valid' ) and datum.is_valid() for datum in self.data ] ) # yapf: disable
