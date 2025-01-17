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
    println!("Hello, world!");

    match run_query("https://www.warcraftlogs.com/api/v2/client")
        .data {
            Some(RequestPoints { rate_limit_data: Some(rate_limit_data)}) => {
                println!("{:?}", rate_limit_data.limit_per_hour);
            }
            _ => {
                println!("none");
            }
        };
}

fn run_query(url: &str) -> cynic::GraphQlResponse<RequestPoints> {
    use cynic::{http::ReqwestBlockingExt, QueryBuilder};

    let query = RequestPoints::build(());
    let token = "";

    reqwest::blocking::Client::new()
        .post(url)
        .header("Authorization", format!("Bearer {}", token))
        .run_graphql(query)
        .unwrap()
}
