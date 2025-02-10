use crate::cache::{init_db, SQL};
use crate::error::Error;
use reqwest::header::HeaderValue;

#[derive(Debug)]
pub struct Token {
    access_token: String,
    token_type: String,
    expires_in: i32,
    expires_at: f64,
}

impl SQL for Token {
    fn select_query() -> &'static str {
        "SELECT * FROM token"
    }

    fn insert_query() -> &'static str {
        "INSERT INTO token (access_token, token_type, expires_in, expires_at) VALUES (?1, ?2, ?3, ?4)"
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
            expires_in: row.get(2)?,
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

pub fn get_token() -> Result<Token, Error> {
    let connection = init_db()?;
    Ok(Token::select(&connection, "")?)
}
