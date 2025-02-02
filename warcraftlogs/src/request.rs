use crate::cache;
use crate::error::Error;
use crate::token;
use cynic::http::ReqwestBlockingExt;

const ENDPOINT: &str = "https://www.warcraftlogs.com/api/v2/client";

// TODO: how do you solve pagination? <- attribute macro :)

fn make_query<T, U>(params: U) -> cynic::Operation<T, U>
where
    U: cynic::QueryVariables,
    T: cynic::QueryBuilder<U>,
{
    T::build(params)
}

fn make_request<T, U>(query: cynic::Operation<T, U>) -> Result<T, Error>
where
    U: cynic::QueryVariables + serde::Serialize,
    T: cynic::QueryBuilder<U> + for<'de> serde::Deserialize<'de> + 'static,
{
    reqwest::blocking::Client::new()
        .post(ENDPOINT)
        .header("Authorization", token::Token::load().unwrap())
        .run_graphql(query)?
        .data
        .ok_or(Error::NoResponseQuery)
}

pub fn run_query_cached<T, U>(params: U) -> Result<T, Error>
where
    U: cynic::QueryVariables + serde::Serialize,
    T: cynic::QueryBuilder<U> + serde::Serialize + for<'a> serde::Deserialize<'a> + 'static,
{
    let query = make_query(params);
    let query_string = serde_json::to_string(&query)?;
    let cached_result = cache::select::<T>(&query_string);
    match cached_result {
        Ok(response) => Ok(response.1.response),
        Err(Error::NoResponseCache(..)) => {
            println!("Cache miss for query: {}", query_string);
            let request = make_request(query)?;
            cache::insert(&query_string, &request)?;
            Ok(request)
        }
        Err(err) => Err(err)
    }
}

pub fn run_query_uncached<T, U>(params: U) -> Result<T, Error>
where
    U: cynic::QueryVariables + serde::Serialize,
    T: cynic::QueryBuilder<U> + serde::Serialize + for<'a> serde::Deserialize<'a> + 'static,
{
    make_request(make_query(params))
}

// implemented by proc macro cache_attribute::cache
#[allow(dead_code)]
pub trait Cache {
    fn run_query<U>(params: U) -> Result<Self, Error>
    where
        U: cynic::QueryVariables + serde::Serialize,
        Self: Sized
            + cynic::QueryBuilder<U>
            + serde::Serialize
            + for<'a> serde::Deserialize<'a>
            + 'static;
}
