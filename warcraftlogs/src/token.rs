use crate::cache::{init_db, SQL};
use crate::error::Error;
use chrono::{DateTime, Utc};
use oauth2::basic::BasicClient;
use oauth2::reqwest;
use oauth2::{
    AuthUrl, AuthorizationCode, ClientId, CsrfToken, PkceCodeChallenge, RedirectUrl, TokenResponse,
    TokenUrl,
};
use open::that_detached;
use reqwest::blocking::ClientBuilder;
use reqwest::header::HeaderValue;
use reqwest::redirect::Policy;
use std::io::{stdin, stdout, Write};

#[derive(Debug, Default)]
pub struct Token {
    access_token: String,
    token_type: String,
    expires_at: DateTime<Utc>,
}

impl SQL for Token {
    fn select_query() -> &'static str {
        "SELECT access_token, token_type, expires_at FROM token"
    }

    fn insert_query() -> &'static str {
        "INSERT INTO token (access_token, token_type, expires_at) VALUES (?1, ?2, ?3)"
    }

    fn create_table() -> &'static str {
        "CREATE TABLE token (id INTEGER PRIMARY KEY, access_token TEXT, token_type TEXT, expires_at TEXT)"
    }

    fn insert(&self, connection: &rusqlite::Connection) -> Result<usize, Error> {
        self._insert(
            connection,
            (&self.access_token, &self.token_type, &self.expires_at),
        )
    }

    fn select(connection: &rusqlite::Connection, _query: &str) -> Result<Self, Error> {
        let mut statement = connection.prepare(Self::select_query())?;
        let responses = statement.query_map((), Self::from_sql)?;
        match responses.last() {
            Some(Ok(last)) => Ok(last),
            Some(Err(err)) => Err(Error::Rusqlite(err)),
            None => Err(Error::NoResponseCache("no token found".to_string())),
        }
    }

    fn from_sql(row: &rusqlite::Row<'_>) -> Result<Self, rusqlite::Error> {
        Ok(Self {
            access_token: row.get(0)?,
            token_type: row.get(1)?,
            expires_at: row.get(2)?,
        })
    }
}

impl TryFrom<Token> for HeaderValue {
    type Error = http::Error;

    fn try_from(value: Token) -> Result<Self, Self::Error> {
        Ok(HeaderValue::from_str(&format!(
            "{} {}",
            value.token_type, value.access_token
        ))?)
    }
}

impl Token {
    pub fn get_token() -> Result<Token, Error> {
        let connection = init_db()?;
        match Token::select(&connection, "") {
            Ok(token) => Ok(token),
            Err(Error::NoResponseCache(..)) => {
                let token = Self::refresh_token()?;
                token.insert(&connection)?;
                Ok(token)
            }
            Err(err) => Err(Error::from(err)),
        }
    }

    pub fn refresh_token() -> Result<Self, Error> {
        let client_id = std::env::var("CLIENT_ID")
            .expect("No CLIENT_ID environment variable.")
            .to_string();
        let auth_uri = "https://www.warcraftlogs.com/oauth/authorize".to_string();
        let token_uri = "https://www.warcraftlogs.com/oauth/token".to_string();
        let redirect_uri = "https://localhost".to_string();

        let client = BasicClient::new(ClientId::new(client_id))
            .set_auth_uri(AuthUrl::new(auth_uri)?)
            .set_token_uri(TokenUrl::new(token_uri)?)
            .set_redirect_uri(RedirectUrl::new(redirect_uri)?);

        let (pkce_challenge, pkce_verifier) = PkceCodeChallenge::new_random_sha256();

        let (auth_url, _) = client
            .authorize_url(CsrfToken::new_random)
            .set_pkce_challenge(pkce_challenge)
            .url();

        println!("Opening in browser: {}", auth_url);

        let _ = that_detached(auth_url.to_string())?;

        print!("Paste contents of code parameter from redirect url: ");

        let _ = stdout().flush();

        let mut input = String::new();
        let _ = stdin().read_line(&mut input)?;

        let http_client = ClientBuilder::new().redirect(Policy::none()).build()?;

        let token_result = client
            .exchange_code(AuthorizationCode::new(input))
            .set_pkce_verifier(pkce_verifier)
            .request(&http_client)
            .expect("Failed to get token");

        println!("{:?}", token_result);

        let access_token: String = token_result.access_token().secret().to_string();

        let token_type = match *token_result.token_type() {
            oauth2::basic::BasicTokenType::Bearer => "Bearer".to_string(),
            _ => panic!("Warcraftlogs v2 API auth changed"),
        };

        let expires_at = match token_result.expires_in() {
            Some(duration) => Utc::now() + duration,
            None => panic!("Invalid duration of token expires_at field"),
        };

        Ok(Self {
            access_token,
            token_type,
            expires_at,
        })
    }
}
