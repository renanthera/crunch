#![allow(dead_code)]
use crate::error::Error;
use cache_attribute::cache;

#[cynic::schema("warcraftlogs")]
mod schema {}

#[cache(false)]
#[cynic(graphql_type = "Query")]
pub struct RequestPoints {
    pub rate_limit_data: Option<RateLimitData>,
}

#[cache(false)]
pub struct RateLimitData {
    pub limit_per_hour: i32,
    pub points_reset_in: i32,
    pub points_spent_this_hour: f64,
}

#[derive(cynic::QueryVariables, Debug)]
pub struct ReportFightsVariables<'a> {
    pub code: Option<&'a str>,
}

#[cache(true)]
#[cynic(graphql_type = "Query", variables = "ReportFightsVariables")]
pub struct ReportFights {
    pub report_data: Option<ReportData>,
}

#[cache(true)]
#[cynic(variables = "ReportFightsVariables")]
pub struct ReportData {
    #[arguments(code: $code)]
    pub report: Option<Report>,
}

#[cache(true)]
pub struct Report {
    pub end_time: f64,
    pub start_time: f64,
    pub fights: Option<Vec<Option<ReportFight>>>,
}

#[cache(true)]
pub struct ReportFight {
    pub end_time: f64,
    pub id: i32,
    pub start_time: f64,
}
