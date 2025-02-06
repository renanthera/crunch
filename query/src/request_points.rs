#![allow(dead_code)]
use cache_attribute::cache;
use cynic;

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
