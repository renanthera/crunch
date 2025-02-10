use crate::cache;
use crate::error::Error;
use crate::token::Token;
use cynic::http::ReqwestBlockingExt;

const ENDPOINT: &str = "https://www.warcraftlogs.com/api/v2/client";

// TODO: how do you solve pagination? <- attribute macro :)
// TODO: auto update schema in build step?

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
        .header("Authorization", Token::get_token()?)
        .run_graphql(query)?
        .data
        .ok_or(Error::NoResponseQuery)
}

fn oneline(query: &str) -> String {
    query
        .split_terminator("\n")
        .map(|str| str.trim())
        .collect::<Vec<&str>>()
        .join(" ")
}

pub fn run_query_cached<T, U>(params: U) -> Result<T, Error>
where
    U: cynic::QueryVariables + serde::Serialize,
    T: cynic::QueryBuilder<U> + serde::Serialize + for<'a> serde::Deserialize<'a> + 'static,
{
    let query = make_query(params);
    let query_str = oneline(&query.query);
    let var_str = oneline(&serde_json::to_string_pretty(&query.variables)?);
    let key = format!("{} {}", query_str, var_str);
    match cache::select::<T>(&key) {
        Ok(response) => Ok(response.response),
        Err(Error::NoResponseCache(..)) => {
            println!("Cache miss.\n{}\nvariables: {}", query_str, var_str);
            let request = make_request(query)?;
            cache::insert(&key, &request)?;
            Ok(request)
        }
        Err(err) => Err(err),
    }
}

pub fn run_query_uncached<T, U>(params: U) -> Result<T, Error>
where
    U: cynic::QueryVariables + serde::Serialize,
    T: cynic::QueryBuilder<U> + serde::Serialize + for<'a> serde::Deserialize<'a> + 'static,
{
    make_request(make_query(params))
}
