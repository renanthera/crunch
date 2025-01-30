use thiserror::Error;

#[derive(Error, Debug)]
pub enum Error {
    #[error(transparent)]
    Cynic(#[from] cynic::GraphQlError),
    #[error(transparent)]
    Reqwest(#[from] cynic::http::CynicReqwestError),
    #[error(transparent)]
    Serde(#[from] serde_json::Error),
    #[error(transparent)]
    Rusqlite(#[from] rusqlite::Error),
    #[error("No response from cache for query {0}")]
    NoResponseCache(String),
    #[error("No response from endpoint for query.")]
    NoResponseQuery,
}
