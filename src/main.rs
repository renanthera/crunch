mod request;
mod token;

#[cynic::schema("warcraftlogs")]
mod schema {}

#[derive(cynic::QueryFragment, Debug)]
#[cynic(graphql_type = "Query")]
pub struct RequestPoints {
    pub rate_limit_data: Option<RateLimitData>,
}

#[derive(cynic::QueryFragment, Debug)]
pub struct RateLimitData {
    pub limit_per_hour: i32,
    pub points_reset_in: i32,
    pub points_spent_this_hour: f64,
}

#[derive(cynic::QueryVariables, Debug)]
pub struct MyQueryVariables<'a> {
    pub code: Option<&'a str>,
}

#[derive(cynic::QueryFragment, Debug)]
#[cynic(graphql_type = "Query", variables = "MyQueryVariables")]
pub struct MyQuery {
    pub report_data: Option<ReportData>,
}

#[derive(cynic::QueryFragment, Debug)]
#[cynic(variables = "MyQueryVariables")]
pub struct ReportData {
    #[arguments(code: $code)]
    pub report: Option<Report>,
}

#[derive(cynic::QueryFragment, Debug)]
pub struct Report {
    pub end_time: f64,
    pub start_time: f64,
    pub fights: Option<Vec<Option<ReportFight>>>,
}

#[derive(cynic::QueryFragment, Debug)]
pub struct ReportFight {
    pub end_time: f64,
    pub id: i32,
    pub start_time: f64,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn points_spent_test() {
        use cynic::QueryBuilder;

        let operation = RequestPoints::build(());

        insta::assert_snapshot!(operation.query);
    }
}

fn main() {
    println!(
        "{:?}",
        request::run_query_h::<RequestPoints>().data.unwrap()
    );
    println!(
        "{:?}",
        request::run_query_g::<MyQuery, MyQueryVariables<'_>>(MyQueryVariables {
            code: Some("d2yTQgjCaWmnYhw8")
        })
        .data
        .unwrap()
    );
}
