#![allow(dead_code)]
use crate::schema;
use cache_attribute::cache;
use cynic;

#[derive(cynic::QueryVariables, Debug)]
pub struct ReportFightsVariables<'a> {
    pub code: Option<&'a str>,
}

#[cache(false)]
#[cynic(graphql_type = "Query", variables = "ReportFightsVariables")]
pub struct ReportFights {
    pub report_data: Option<ReportData>,
}

#[cache(false)]
#[cynic(variables = "ReportFightsVariables")]
pub struct ReportData {
    #[arguments(code: $code)]
    pub report: Option<Report>,
}

#[cache(false)]
pub struct Report {
    pub end_time: f64,
    pub start_time: f64,
    pub fights: Option<Vec<Option<ReportFight>>>,
}

#[cache(false)]
pub struct ReportFight {
    pub end_time: f64,
    pub id: i32,
    pub start_time: f64,
}
