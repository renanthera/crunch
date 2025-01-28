// use crate::cache;
use crate::token;

const ENDPOINT: &str = "https://www.warcraftlogs.com/api/v2/client";

// TODO: replace pub interface with a macro for variadic support
// TODO: query caching
// TODO: how do you dynamically solve pagination?

pub fn make_query<T, U>(params: U) -> cynic::Operation<T, U>
where
    U: cynic::QueryVariables,
    T: cynic::QueryBuilder<U>,
{
    T::build(params)
}

pub fn make_request<T, U>(query: cynic::Operation<T, U>) -> cynic::GraphQlResponse<T>
where
    U: cynic::QueryVariables + serde::Serialize,
    T: cynic::QueryBuilder<U> + for<'de> serde::Deserialize<'de> + 'static,
{
    use cynic::http::ReqwestBlockingExt;
    reqwest::blocking::Client::new()
        .post(ENDPOINT)
        .header("Authorization", token::Token::load().unwrap())
        .run_graphql(query)
        .unwrap()
}

pub fn run_query_variables<T, U>(params: U) -> cynic::GraphQlResponse<T>
where
    U: cynic::QueryVariables + serde::Serialize,
    T: cynic::QueryBuilder<U> + for<'de> serde::Deserialize<'de> + 'static,
{
    let query = make_query(params);
    let query_string = serde_json::to_string(&query).unwrap();
    // query.query -> String(query sent to server)

    make_request(query)
}

pub fn run_query<T>() -> cynic::GraphQlResponse<T>
where
    T: cynic::QueryBuilder<()> + for<'de> serde::Deserialize<'de> + 'static,
{
    run_query_variables(())
}
