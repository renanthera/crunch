use chrono::prelude::*;
use rusqlite::{Connection, OpenFlags};
use thiserror::Error;

// TODO: reorganize to make it a bit more consistent
// TODO: are both traits good to have?
// TODO: close db connection
// TODO: compress response - does this make ToSql for <T> better? can serialization be done generically by serde -> gzip it?
// TODO: increment hits, update hit timestamp
// TODO: make types less horrible, properly use `use`

const DBPATH: &str = "cache.db";
const CREATE_QUERY_TABLE: &str = "CREATE TABLE query (id INTEGER PRIMARY KEY, query TEXT, response BLOB, hits INT, time_first_request CHAR(50), time_last_request CHAR(50))";
const CREATE_RESPONSE_TABLE: &str = "CREATE TABLE response (id INTEGER PRIMARY KEY, response BLOB)";
const INSERT_QUERY: &str = "INSERT INTO query (query, hits, time_first_request, time_last_request) VALUES (?1, ?2, ?3, ?4)";
const INSERT_RESPONSE: &str = "INSERT INTO response (id, response) VALUES (?1, ?2)";
const SELECT_QUERY: &str = "SELECT * FROM query WHERE query = (?1)";
const SELECT_RESPONSE: &str = "SELECT * FROM response WHERE id = (?)";

fn init_db() -> Result<Connection, rusqlite::Error> {
    if let Ok(conn) = Connection::open_with_flags(
        DBPATH,
        OpenFlags::SQLITE_OPEN_READ_WRITE | OpenFlags::SQLITE_OPEN_NO_MUTEX,
    ) {
        // check to make sure the correct tables exist
        return Ok(conn);
    }

    match Connection::open(DBPATH) {
        Ok(conn) => {
            conn.execute(CREATE_QUERY_TABLE, ())?;
            conn.execute(CREATE_RESPONSE_TABLE, ())?;
            Ok(conn)
        }
        Err(err) => Err(err),
    }
}

#[derive(Error, Debug)]
pub enum Error {
    #[error(transparent)]
    Rusqlite(#[from] rusqlite::Error),
    #[error("No response found for query ({0}).")]
    NoResponse(String),
}

#[derive(Debug)]
pub struct Query {
    id: i32,
    query: String,
    hits: i32,
    time_first_request: DateTime<Utc>,
    time_last_request: DateTime<Utc>,
}

#[derive(Debug)]
pub struct Response<T>
where
    T: rusqlite::types::FromSql + rusqlite::types::ToSql,
{
    id: i32,
    response: T,
}

pub trait SQL: Sized {
    fn select_query() -> String;
    fn from_sql(row: &rusqlite::Row<'_>) -> Result<Self, rusqlite::Error>;
}

impl SQL for Query {
    fn select_query() -> String {
        SELECT_QUERY.to_string()
    }

    fn from_sql(row: &rusqlite::Row<'_>) -> Result<Query, rusqlite::Error> {
        Ok(Query {
            id: row.get(0)?,
            query: row.get(1)?,
            hits: row.get(3)?,
            time_first_request: row.get(4)?,
            time_last_request: row.get(5)?,
        })
    }
}

impl<T> SQL for Response<T>
where
    T: rusqlite::types::FromSql + rusqlite::types::ToSql,
{
    fn select_query() -> String {
        SELECT_RESPONSE.to_string()
    }

    fn from_sql(row: &rusqlite::Row<'_>) -> Result<Response<T>, rusqlite::Error> {
        Ok(Response::<T> {
            id: row.get(0)?,
            response: row.get(1)?,
        })
    }
}

pub trait Cache
where
    Self: Sized + SQL,
{
    fn select(connection: &Connection, query: &str) -> Result<Self, Error> {
        let mut statement = connection.prepare(&Self::select_query())?;
        let responses = statement.query_map((query,), <Self as SQL>::from_sql)?;
        match responses.last() {
            Some(Ok(last)) => Ok(last),
            Some(Err(err)) => Err(Error::Rusqlite { 0: err }),
            None => Err(Error::NoResponse {
                0: query.to_string(),
            }),
        }
    }

    fn insert(&self, connection: &Connection) -> Result<usize, Error>;
}

impl Cache for Query {
    fn insert(&self, connection: &Connection) -> Result<usize, Error> {
        let mut statement = connection.prepare(INSERT_QUERY)?;
        Ok(statement.execute((&self.query, 0, Utc::now(), Utc::now()))?)
    }
}

impl<T> Cache for Response<T>
where
    T: rusqlite::types::FromSql + rusqlite::types::ToSql,
{
    fn insert(&self, connection: &Connection) -> Result<usize, Error> {
        let mut statement = connection.prepare(INSERT_RESPONSE)?;
        Ok(statement.execute((&self.id, &self.response))?)
    }
}

pub fn cache<T>(query: String, response: T) -> Result<(), Error>
where
    T: rusqlite::types::FromSql + rusqlite::types::ToSql,
{
    let connection = init_db()?;
    let entry = Query {
        id: 0,
        query: query.clone(),
        hits: 0,
        time_first_request: Utc::now(),
        time_last_request: Utc::now(),
    };
    entry.insert(&connection)?;
    let inserted_query = Query::select(&connection, &query)?;
    let response = Response::<T> {
        id: inserted_query.id,
        response,
    };
    response.insert(&connection)?;
    Ok(())
}

pub fn query<T>(query: String) -> Result<(Query, Response<T>), Error>
where
    T: rusqlite::types::FromSql + rusqlite::types::ToSql,
{
    let connection = init_db()?;
    let query = <Query as Cache>::select(&connection, &query)?;
    let response = <Response<T> as Cache>::select(&connection, &(query.id.to_string()))?;
    Ok((query, response))
}
