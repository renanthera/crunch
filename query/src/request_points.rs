#![allow(dead_code)]
use crate::schema;
use cache_attribute::cache;
use cynic;

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
