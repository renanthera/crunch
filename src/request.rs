use crate::token;

const ENDPOINT: &str = "https://www.warcraftlogs.com/api/v2/client";

pub fn run_query_g<T, U>(params: U) -> cynic::GraphQlResponse<T>
where
    U: cynic::QueryVariables + serde::Serialize,
    T: cynic::QueryBuilder<U> + for<'de> serde::Deserialize<'de> + 'static,
{
    use cynic::http::ReqwestBlockingExt;

    let query = T::build(params);
    reqwest::blocking::Client::new()
        .post(ENDPOINT)
        .header("Authorization", token::Token::load().unwrap())
        .run_graphql(query)
        .unwrap()
}

pub fn run_query_h<T>() -> cynic::GraphQlResponse<T>
where
    T: cynic::QueryBuilder<()> + for<'de> serde::Deserialize<'de> + 'static,
{
    run_query_g::<T, ()>(())
}
