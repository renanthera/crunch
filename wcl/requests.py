from os import path
from . import caching, query, token

import requests
import json
from requests.exceptions import HTTPError

class Request:
  v2_endpoint = 'https://www.warcraftlogs.com/api/v2/client'
  cache = caching.Cache()
  token = token.Token()

  DEBUG = False

  def __init__( self, query ):
    self.query = query

    if self.query.cacheable:
      self.data = self.cache.get_artifact( self.query.string )
      if self.data:
        if self.DEBUG:
          print( 'read', self.query.string, 'from cache' )
        return

    self.data = self.get_request()
    if self.query.cacheable:
      self.cache.put_artifact( self.query.string, self.data )

  def get_request( self ):
    def https_request( retry=0 ):
      if self.DEBUG:
        print( 'requesting', self.query.stringify() )
      try:
        req = requests.post(
          self.v2_endpoint,
          headers={
            'Authorization': self.token.auth
          },
          data={
            'query': self.query.stringify()
          }
        )

        resp = json.loads( req.text )
        if self.DEBUG:
          if resp.get( 'error', '' ) == 'Unauthenticated.':
            if retry:
              print( 'Failed. Already retried...' )
              return
            print( 'Unauthenticated. Attempting to obtain new token and retry...' )
            self.token.get_token()
            return https_request( retry=1 )
        return resp
      except HTTPError as err:
        print( f'HTTP error occurred: {err}' )
        raise SystemExit

    def get_path( node ):
      if node.get( 'fields' ) is None:
        return node.get( 'name' )
      if any( [ field.get( 'fields' ) or field.get( 'args' ) for field in node.get( 'fields' ) ] ):
        child_fields = [ get_path( field ) for field in node.get( 'fields' ) ]
        child_fields = child_fields[ 0 ] if isinstance( child_fields[ 0 ], list ) else child_fields
        return [ node.get( 'name' ), *child_fields ]
      return node.get( 'name' )

    def drill_down( data, keys ):
      if len( keys ) > 0 and data is not None:
        return drill_down( data.get( keys[ 0 ] ), keys[ 1: ] )
      return data

    resp = https_request()

    # print('path', [get_path(self.query.tree)])
    # print(json.dumps(resp, indent=2))

    if resp.get( 'errors' ): # pyright: ignore
      print( json.dumps( resp, indent=2 ) )
      raise SystemExit

    path = get_path( self.query.tree )
    body = drill_down(
      resp.get( 'data' ), # pyright: ignore
      path if type(path) is list else [path]
    )

    # print(json.dumps(body, indent=2))

    if isinstance( body, dict ):
      if any( self.query.paginator.values() ) and body.get(
          self.query.paginator.get( 'paginationField' ) ):
        self.query.update( {
          self.query.paginator.get( 'overrides' ):
          body.get( self.query.paginator.get( 'paginationField' ) )
        } )

        body[ 'data' ] += self.get_request().get( 'data' )

    return body

  # TODO: better object resolution
