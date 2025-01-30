use crate::cache;
use crate::error::Error;
use crate::token;
use cynic::http::ReqwestBlockingExt;

const ENDPOINT: &str = "https://www.warcraftlogs.com/api/v2/client";

// TODO: replace pub interface with a macro for variadic support
// TODO: query caching
// TODO: how do you solve pagination?

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

// TODO: determine if $t implements query::DoCache to control whether or not
// response gets cached
pub fn run_query_variables<T, U>(params: U) -> Result<T, Error>
where
    U: cynic::QueryVariables + serde::Serialize,
    T: crate::query::DoCache + std::fmt::Debug + cynic::QueryBuilder<U> + serde::Serialize + for<'de> serde::Deserialize<'de> + 'static,
{
    let query = make_query(params);
    let query_string = serde_json::to_string(&query)?;
    let cached_result = cache::select::<T>(&query_string);
    match cached_result {
        Ok(response) => Ok(response.1.response),
        Err(Error::NoResponseCache(..)) => {
            let request = make_request(query)?;
            cache::insert(&query_string, &request)?;
            Ok(request)
        }
        Err(err) => Err(err),
    }
}

// pub fn run_query_variables<T, U>(params: U) -> Result<T, Error>
// where
//     U: cynic::QueryVariables + serde::Serialize,
//     T: std::fmt::Debug + cynic::QueryBuilder<U> + serde::Serialize + for<'de> serde::Deserialize<'de> + 'static,
// {
//     let query = make_query(params);
//     let query_string = serde_json::to_string(&query)?;
//     make_request(query)?
// }


macro_rules! run_query {
    ( $t:ty, $x:expr ) => {
        $crate::request::run_query_variables::<$t>(x)
    };
    ( $t:ty ) => {
        $crate::request::run_query_variables::<$t, ()>(())
    };
}

pub(crate) use run_query;
