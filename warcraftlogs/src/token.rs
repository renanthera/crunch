use crate::error::Error;
use serde::{Deserialize, Serialize};
use std::fs::File;
use std::io::Read;

// TODO: move this to database

const TOKENPATH: &str = "token.tk";

#[derive(Deserialize, Serialize, Debug)]
pub struct Token {
    access_token: String,
    token_type: String,
    expires_in: i32,
    expires_at: f64,
}

impl Token {
    fn fmt(&self) -> String {
        format!("{} {}", self.token_type, self.access_token)
    }

    pub fn load() -> Result<String, Error> {
        let mut file = File::open(TOKENPATH)?;
        let mut contents = String::new();
        file.read_to_string(&mut contents)?;
        Ok(serde_json::from_str::<Self>(&contents)?.fmt())
    }
}
