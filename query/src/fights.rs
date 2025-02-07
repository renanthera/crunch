#![allow(dead_code)]
use cache_attribute::cache;
use cynic;

#[cynic::schema("warcraftlogs")]
mod schema {}

#[derive(cynic::QueryVariables, Debug)]
pub struct ReportFightsVariables<'a> {
    pub code: Option<&'a str>,
}

#[cache(true)]
#[cynic(
    graphql_type = "Query",
    variables = "ReportFightsVariables",
    schema = "warcraftlogs"
)]
pub struct ReportFights {
    pub report_data: Option<ReportData>,
}

#[cache(true)]
#[cynic(variables = "ReportFightsVariables", schema = "warcraftlogs")]
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
