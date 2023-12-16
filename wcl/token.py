import time
import json
import pickle

from requests.exceptions import HTTPError
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

class Token:
  token_url = 'https://www.warcraftlogs.com/oauth/token'
  token_filename = 'token.tk'
  credentials_filename = 'credentials'

  def __init__( self ):
    self.read_token()

    if self.token is None:
      self.get_token()

    if self.expiry - 60 * 60 * 24 < time.time():
      self.get_token()

  def load_token( self ):
    if self.token:
      self.expiry = self.token.get( 'expires_at' )
      self.auth = self.token.get( 'token_type' ) + ' ' + self.token.get( 'access_token' )

  def read_token( self ):
    try:
      with open( self.token_filename, 'r' ) as handle:
        data = json.load( handle )
      self.token = data
      self.load_token()
    except Exception as err:
      print( f'Failed to load token: {err}' )
      self.token = None

  def write_token( self ):
    json_object = json.dumps( self.token, indent=2 )
    with open( self.token_filename, 'w' ) as handle:
      handle.write( json_object )

  def read_credentials( self ):
    with open( self.credentials_filename, 'rb' ) as handle:
      data = json.load( handle )
    return data.get('clientID'), data.get('clientSecret')

  def get_token( self ):
    try:
      client_id, client_secret = self.read_credentials()
      client = BackendApplicationClient( client_id=client_id )
      oauth_session = OAuth2Session( client=client )
      self.token = oauth_session.fetch_token(
        token_url=self.token_url,
        client_id=client_id,
        client_secret=client_secret
      )
      self.load_token()
      self.write_token()
    except HTTPError as http_err:
      print( f'HTTP error occurred: {http_err}' )
      raise SystemExit
    except Exception as err:
      print( f'Other error occurred: {err}' )
      raise SystemExit
