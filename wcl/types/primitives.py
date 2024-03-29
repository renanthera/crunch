# GQL PRIMITIVE TYPES

from inspect import isclass

class GQL_KIND:
  data = None

  def update( self, data ):
    self.data = data
    return self.is_valid()

  def is_valid( self ):
    assert False, f'{type(self).__name__} does not contain valid data ({self.data}, {type(self.data)})'
    return True

  def __str__( self ):
    self.is_valid()
    return str( self.data )

class GQL_SCALAR( GQL_KIND ):
  base_type = None

  def is_valid( self ):
    assert isclass( self.base_type ), f'{self.base_type} is not a class'
    assert isinstance( self.data, self.base_type ), f'{type(self).__name__} does not contain valid data ({self.data}, {type(self.data)})'
    return True

class GQL_ENUM( GQL_KIND ):
  enum_values = []

  def is_valid( self ):
    assert self.data in self.enum_values, f'{self.data} not found in permitted values ({self.enum_values})'
    return True

class GQL_OBJECT( GQL_KIND ):
  fields = []

  def update( self ):
    # ...update data
    return self.is_valid()

  def is_valid( self ):
    # ...assert if invalid
    return True

  def __str__( self ):
    self.is_valid()
    # ...stringify

# GQL TYPE KINDS
class GQL_NON_NULL( GQL_KIND ):
  def is_valid( self ):
    assert self.data is not None
    assert isinstance( self.data, GQL_KIND ), f'type {type(self).__name__} is not a subtype of GQL_KIND'
    assert self.data.is_valid()
    return True

class GQL_LIST( GQL_KIND ):
  def is_valid( self ):
    assert isinstance( self.data, list ), f'{type(self).__name__} data is not a list ({self.data}, {type(self.data)})'
    assert all( [ isinstance( datum, GQL_KIND ) and datum.is_valid() for datum in self.data ] ), f'{type(self).__name__} does not contain valid data {", ".join([f"{datum}:{type(datum)}"for datum in self.data])}' # yapf: disable
    return True

  def __str__( self ):
    self.is_valid()
    assert isinstance( self.data, list ) # redundant, silences linter
    return '[' + ', '.join( [ str( datum ) for datum in self.data ] ) + ']'
