use thiserror::Error;

#[derive(Error, Debug)]
pub enum Error {
    #[error(transparent)]
    Cynic(#[from] cynic::GraphQlError),
    #[error(transparent)]
    ReqwestCynic(#[from] cynic::http::CynicReqwestError),
    #[error(transparent)]
    ReqestHeader(#[from] reqwest::header::InvalidHeaderValue),
    #[error(transparent)]
    Reqwest(#[from] reqwest::Error),
    #[error(transparent)]
    Oauth2Parse(#[from] oauth2::url::ParseError),
    #[error(transparent)]
    Serde(#[from] serde_json::Error),
    #[error(transparent)]
    Rusqlite(#[from] rusqlite::Error),
    #[error(transparent)]
    Std(#[from] std::io::Error),
    #[error("No response from cache for query {0}")]
    NoResponseCache(String),
    #[error("No response from endpoint for query.")]
    NoResponseQuery,
}
