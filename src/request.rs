use crate::cache;
use crate::token;
use thiserror::Error;

const ENDPOINT: &str = "https://www.warcraftlogs.com/api/v2/client";

// TODO: replace pub interface with a macro for variadic support
// TODO: query caching
// TODO: how do you dynamically solve pagination?

#[derive(Error, Debug, PartialEq)]
pub enum Error {
    #[error(transparent)]
    Cynic(#[from] cynic::GraphQlError),
    #[error(transparent)]
    Reqwest(#[from] cynic::http::CynicReqwestError),
}

pub fn make_query<T, U>(params: U) -> cynic::Operation<T, U>
where
    U: cynic::QueryVariables,
    T: cynic::QueryBuilder<U>,
{
    T::build(params)
}

pub fn make_request<T, U>(query: cynic::Operation<T, U>) -> Result<cynic::GraphQlResponse<T>, Error>
where
    U: cynic::QueryVariables + serde::Serialize,
    T: cynic::QueryBuilder<U> + for<'de> serde::Deserialize<'de> + 'static,
{
    use cynic::http::ReqwestBlockingExt;
    Ok(reqwest::blocking::Client::new()
        .post(ENDPOINT)
        .header("Authorization", token::Token::load().unwrap())
        .run_graphql(query)?)
}

pub fn run_query_variables<T, U>(params: U) -> Result<cynic::GraphQlResponse<T>, Error>
where
    U: cynic::QueryVariables + serde::Serialize,
    T: cynic::QueryBuilder<U> + for<'de> serde::Deserialize<'de> + 'static,
{
    let query = make_query(params);
    let query_string = serde_json::to_string(&query)?;
    // query.query -> String(query sent to server)
    match cache::select::<cynic::GraphQlResponse<T>>(query_string) {
        Ok(response) => Ok(response.1.response),
        Err(ref err) => match err {
            cache::Error::NoResponse(..) => Ok(make_request(query)),
            _ => Err(err),
        },
    }

    // make_request(query)
}

pub fn run_query<T>() -> cynic::GraphQlResponse<T>
where
    T: cynic::QueryBuilder<()> + for<'de> serde::Deserialize<'de> + 'static,
{
    run_query_variables(())
}
