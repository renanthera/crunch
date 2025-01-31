use crate::error::Error;
use chrono::{DateTime, Utc};
use rusqlite::Error as RusqliteError;
use rusqlite::{Connection, OpenFlags, Row};
use serde::{Deserialize, Serialize};
use serde_json::{from_slice, to_vec};

// TODO: close db connection
// TODO: compress response
// TODO: increment hits, update hit timestamp

const DBPATH: &str = "cache.db";
const CREATE_QUERY_TABLE: &str = "CREATE TABLE query (id INTEGER PRIMARY KEY, query TEXT, hits INT, time_first_request CHAR(50), time_last_request CHAR(50))";
const CREATE_RESPONSE_TABLE: &str = "CREATE TABLE response (id INTEGER PRIMARY KEY, response TEXT)";
const INSERT_QUERY: &str = "INSERT INTO query (query, hits, time_first_request, time_last_request) VALUES (?1, ?2, ?3, ?4)";
const INSERT_RESPONSE: &str = "INSERT INTO response (id, response) VALUES (?1, ?2)";
const SELECT_QUERY: &str = "SELECT * FROM query WHERE query = (?1)";
const SELECT_RESPONSE: &str = "SELECT * FROM response WHERE id = (?)";

fn init_db() -> Result<Connection, RusqliteError> {
    if let Ok(conn) = Connection::open_with_flags(
        DBPATH,
        OpenFlags::SQLITE_OPEN_READ_WRITE | OpenFlags::SQLITE_OPEN_NO_MUTEX,
    ) {
        // TODO: check to make sure the correct tables exist, not just a db
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

#[allow(dead_code)]
#[derive(Debug)]
pub struct Query {
    pub id: i32,
    pub query: String,
    pub hits: i32,
    pub time_first_request: DateTime<Utc>,
    pub time_last_request: DateTime<Utc>,
}

#[allow(dead_code)]
#[derive(Debug)]
pub struct Response<T>
where
    T: Serialize + for<'a> Deserialize<'a>,
{
    pub id: i32,
    pub response: T,
}

#[derive(Debug, Serialize, Deserialize)]
struct InternalResponse {
    id: i32,
    response: Vec<u8>,
}

trait SQL
where
    Self: Sized,
{
    fn select_query() -> &'static str;

    fn insert_query() -> &'static str;

    fn from_sql(row: &Row<'_>) -> Result<Self, RusqliteError>;

    fn insert(&self, connection: &Connection) -> Result<usize, Error>;

    fn select(connection: &Connection, query: &str) -> Result<Self, Error> {
        let mut statement = connection.prepare(Self::select_query())?;
        let responses = statement.query_map((query,), Self::from_sql)?;
        match responses.last() {
            Some(Ok(last)) => Ok(last),
            Some(Err(err)) => Err(Error::Rusqlite { 0: err }),
            None => Err(Error::NoResponseCache {
                0: query.to_string(),
            }),
        }
    }
}

impl SQL for Query {
    fn select_query() -> &'static str {
        SELECT_QUERY
    }

    fn insert_query() -> &'static str {
        INSERT_QUERY
    }

    fn from_sql(row: &Row<'_>) -> Result<Query, RusqliteError> {
        Ok(Query {
            id: row.get(0)?,
            query: row.get(1)?,
            hits: row.get(3)?,
            time_first_request: row.get(4)?,
            time_last_request: row.get(5)?,
        })
    }

    fn insert(&self, connection: &Connection) -> Result<usize, Error> {
        let mut statement = connection.prepare(Self::insert_query())?;
        Ok(statement.execute((&self.query, 0, Utc::now(), Utc::now()))?)
    }
}

impl SQL for InternalResponse {
    fn select_query() -> &'static str {
        SELECT_RESPONSE
    }

    fn insert_query() -> &'static str {
        INSERT_RESPONSE
    }

    fn from_sql(row: &Row<'_>) -> Result<InternalResponse, RusqliteError> {
        Ok(InternalResponse {
            id: row.get(0)?,
            response: row.get(1)?,
        })
    }

    fn insert(&self, connection: &Connection) -> Result<usize, Error> {
        let mut statement = connection.prepare(Self::insert_query())?;
        Ok(statement.execute((&self.id, &self.response))?)
    }
}

pub fn insert<T>(query: &String, response: &T) -> Result<(), Error>
where
    T: Serialize + for<'a> Deserialize<'a>,
{
    let connection = init_db()?;
    let q = Query {
        id: 0,
        query: query.clone(),
        hits: 0,
        time_first_request: Utc::now(),
        time_last_request: Utc::now(),
    };
    q.insert(&connection)?;
    let id = Query::select(&connection, &query)?.id;
    let response = InternalResponse {
        id,
        response: to_vec(&response)?,
    };
    response.insert(&connection)?;
    Ok(())
}

pub fn select<T>(query: &String) -> Result<(Query, Response<T>), Error>
where
    T: Serialize + for<'a> Deserialize<'a>,
{
    let connection = init_db()?;
    let query = Query::select(&connection, &query)?;
    let ir = InternalResponse::select(&connection, &(query.id.to_string()))?;
    let response = Response::<T> {
        id: ir.id,
        response: from_slice(&ir.response)?,
    };
    Ok((query, response))
}
