use crate::cache::{init_db, SQL};
use crate::error::Error;
use oauth2::basic::BasicClient;
use oauth2::reqwest;
use oauth2::{
    AuthUrl, AuthorizationCode, ClientId, CsrfToken, PkceCodeChallenge, RedirectUrl, TokenUrl, TokenResponse
};
use open::that_detached;
use reqwest::blocking::ClientBuilder;
use reqwest::header::HeaderValue;
use reqwest::redirect::Policy;
use std::io::{stdin, stdout, Write};
use chrono::{DateTime, Utc};

#[derive(Debug, Default)]
pub struct Token {
    access_token: String,
    token_type: String,
    // expires_in: chrono::TimeDelta, TODO: serialize TimeDelta somehow
    expires_at: DateTime<Utc>,
}

impl SQL for Token {
    fn select_query() -> &'static str {
        "SELECT * FROM token"
    }

    fn insert_query() -> &'static str {
        // "INSERT INTO token (access_token, token_type, expires_in, expires_at) VALUES (?1, ?2, ?3, ?4)"
        "INSERT INTO token (access_token, token_type, expires_at) VALUES (?1, ?2, ?3, ?4)"
    }

    fn create_table() -> &'static str {
        "CREATE TABLE token (id INTEGER PRIMARY KEY, access_token TEXT, token_type TEXT, expires_at TEXT)"
    }

    fn insert(&self, connection: &rusqlite::Connection) -> Result<usize, Error> {
        self._insert(
            connection,
            (
                &self.access_token,
                &self.token_type,
                &self.expires_in,
                &self.expires_at,
            ),
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
            // expires_in: row.get(2)?,
            expires_at: row.get(3)?,
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
        Ok(Token::select(&connection, "")?)
    }

    pub fn refresh_token() -> Result<Self, Error> {
        let client_id = "9e2d1773-fba5-4376-b99e-ebcb6699d11d".to_string();
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
            _ => todo!()
        };

        // let expires_in = match token_result.expires_in() {
        //     // Some(duration) => DateTime::from_timestamp( duration.as_secs().try_into().unwrap(), 0).unwrap(),
        //     Some(duration) => Utc::now() + duration,
        //     None => todo!()
        // };

        let expires_at = match token_result.expires_in() {
            Some(duration) => Utc::now() + duration,
            None => todo!()
        };

        Ok(Self {
            access_token,
            token_type,
            // expires_in,
            expires_at,
        })
    }
}
