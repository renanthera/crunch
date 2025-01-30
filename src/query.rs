#![allow(dead_code)]

#[cynic::schema("warcraftlogs")]
mod schema {}

pub trait DoCache {}

#[derive(cynic::QueryFragment, Debug, serde::Serialize)]
#[cynic(graphql_type = "Query")]
#[serde(rename_all = "camelCase")]
pub struct RequestPoints {
    pub rate_limit_data: Option<RateLimitData>,
}

impl DoCache for RequestPoints {}

// impl cache::Cache for RequestPoints {}

#[derive(cynic::QueryFragment, Debug, serde::Serialize)]
#[serde(rename_all = "camelCase")]
pub struct RateLimitData {
    pub limit_per_hour: i32,
    pub points_reset_in: i32,
    pub points_spent_this_hour: f64,
}
// impl cache::Cache for RateLimitData {}

#[derive(cynic::QueryVariables, Debug)]
pub struct ReportFightsVariables<'a> {
    pub code: Option<&'a str>,
}

#[derive(cynic::QueryFragment, Debug)]
#[cynic(graphql_type = "Query", variables = "ReportFightsVariables")]
pub struct ReportFights {
    pub report_data: Option<ReportData>,
}

#[derive(cynic::QueryFragment, Debug)]
#[cynic(variables = "ReportFightsVariables")]
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
