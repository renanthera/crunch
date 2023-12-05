from . import caching

import requests
import json
import pickle
import time
from requests.exceptions import HTTPError
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

class Token:
  tokenURI = 'https://www.warcraftlogs.com/oauth/token'

  tokenFilename = 'token.tk'
  credentialsFilename = 'credentials'

  def __init__( self ):
    self.token = self.read()
    # if failed to load or expiring in less than a day, acquire new token
    if ( self.token is None ):
      print( f'Token file missing, generating new token...' )
      self.token = self.get()
    if ( self.token.get( 'expires_at' ) - 3600 < time.time() ):
      expiry_time = self.token.get( 'expires_at' ) - time.time()
      print( f'Token expiring in {expiry_time}, generating new token...' )
      self.token = self.get()

  def read( self ):
    try:
      with open( self.tokenFilename, 'rb' ) as handle:
        data = handle.read()
      return pickle.loads( data )
    except Exception as err:
      print( f'Failed to load token, error occurred: {err}' )
      return None

  def write( self ):
    file = open( self.tokenFilename, 'wb' )
    pickle.dump( self.token, file )
    file.close()

  def get( self ):
    try:
      clientID, clientSecret = self.loadCredentials()
      client = BackendApplicationClient( client_id=clientID )
      oauth = OAuth2Session( client=client )
      token = oauth.fetch_token(
        token_url=self.tokenURI,
        client_id=clientID,
        client_secret=clientSecret
      )
      self.write()
      return token
    except HTTPError as http_err:
      print( f'HTTP error occurred: {http_err}' )
      raise SystemExit
    except Exception as err:
      print( f'Other error occurred: {err}' )
      raise SystemExit

  def loadCredentials( self ):
    with open( self.credentialsFilename, 'rb' ) as handle:
      data = handle.read()
    data = str( data ).split( '\'' )
    return data[ 1 ], data[ 3 ]

class Request:
  v2endpoint = 'https://www.warcraftlogs.com/api/v2/client'
  cache = caching.Cache()

  def __init__( self, query ):
    self.token = Token()
    self.query = query

    if self.query.cache:
      self.data = self.cache.get_artifact( self.query.query )
      if self.data:
        print( 'read', self.query.query[ :40 ] + '...', 'from cache' )
        return

    self.data = []
    self.get_entire_request()
    if self.query.cache:
      self.cache.put_artifact( self.query.query, self.data )
    return

  def get_entire_request( self ):
    body = self.get_request()

    # i hate this solution, but i don't have any idea how to come up with something better right now
    try:
      payload = body[ 'data' ][ 'reportData' ][ 'report' ][ self.query.kind ]
    except:
      if body[ 'data' ][ 'rateLimitData' ][ 'pointsSpentThisHour' ]:
        self.data = body[ 'data' ][ 'rateLimitData' ][ 'pointsSpentThisHour' ]
        print( str( self.data ) + '/3600' )
        return
      print( 'failed:' )
      print( body )
      return
    if isinstance( payload, dict ):
      self.data.append( payload.get( 'data' ) )
      if payload.get( 'nextPageTimestamp' ):
        self.query.update_query( {
          'startTime': payload.get( 'nextPageTimestamp' )
        } )
        self.get_entire_request()
        return
      return
    else:
      self.data = payload
    return

  def get_request( self, failed=0 ):
    print( 'requesting', self.query.query )
    try:
      request = requests.post(
        self.v2endpoint,
        headers={
          'Authorization': "Bearer " + self.token.token[ 'access_token' ]
        },
        data={
          'query': self.query.query
        }
      )
      if ( request.text == "{\"error\":\"Unauthenticated.\"}" ):
        if ( failed == 1 ):
          print( 'Already failed once. Something\'s borked, fix it yourself.' )
          return -1
        print( 'Unauthenticated. Attempting to obtain new token and re-run query.' )
        self.token.get()
        return self.get_request( failed=1 )
      return json.loads( request.text )
    except HTTPError as http_err:
      print( f'HTTP error occurred: {http_err}' )
      raise SystemExit
