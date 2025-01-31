#![allow(dead_code)]

// use crate::cache::{Query, Response};
use crate::error::Error;

#[cynic::schema("warcraftlogs")]
mod schema {}

pub trait Cache {
    fn run_query<U>(params: U) -> Result<Self, Error>
    where
        U: cynic::QueryVariables + serde::Serialize,
        Self: serde::Serialize + for<'a> serde::Deserialize<'a>;
}

#[derive(cynic::QueryFragment, Debug, serde::Serialize)]
#[cynic(graphql_type = "Query")]
#[serde(rename_all = "camelCase")]
pub struct RequestPoints {
    pub rate_limit_data: Option<RateLimitData>,
}

#[derive(cynic::QueryFragment, Debug, serde::Serialize)]
#[serde(rename_all = "camelCase")]
pub struct RateLimitData {
    pub limit_per_hour: i32,
    pub points_reset_in: i32,
    pub points_spent_this_hour: f64,
}

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
