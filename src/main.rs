mod cache;
mod query;
mod request;
mod token;

use thiserror::Error;

#[derive(Debug, serde::Serialize)]
struct Temp {
    body: String,
}

// #[derive(Error, Debug)]
// pub enum ParseTempError {
//     #[error(transparent)]
//     Rusqlite(#[from] rusqlite::Error),
//     #[error("asdf")]
//     NoParse,
// }

// // this is kinda misery x3
// impl rusqlite::types::ToSql for Temp {
//     fn to_sql(&self) -> rusqlite::Result<rusqlite::types::ToSqlOutput<'_>> {
//         Ok(self.body.clone().into())
//     }
// }

// impl rusqlite::types::FromSql for Temp {
//     fn column_result(value: rusqlite::types::ValueRef<'_>) -> rusqlite::types::FromSqlResult<Self> {
//         value
//             .as_str()?
//             .parse()
//             .map_err(|e| rusqlite::types::FromSqlError::Other(Box::new(e)))
//     }
// }

// impl std::str::FromStr for Temp {
//     type Err = ParseTempError;
//     fn from_str(s: &str) -> Result<Self, Self::Err> {
//         Ok(Temp {
//             body: String::from(s),
//         })
//     }
// }

fn main() {
    let body = Temp {
        body: "12345asdfjkl".to_string(),
    };

    // let v = cache::cache("asdf".to_string(), body);
    // let q = cache::query::<Temp>("asdf".to_string());
    // println!("{:?}", v);
    // println!("{:?}", q);

    // let query = request::make_query::<query::RequestPoints, _>(());
    // let response = request::run_query::<query::RequestPoints>();
    // let binding = response.data.unwrap();
    // let rv = binding.cache(serde_json::to_string(&query).unwrap());
    // println!("{:#?}", rv);

    // ptypeof(&response);
    // ptypeof(&(response.data));
    // let q = cache::Query::new(
    //     serde_json::to_string(&query).unwrap(),
    //     response.data.unwrap());
    // println!("{:#?}", q.unwrap());

    // println!("{:?}", q);
    // println!("{}", serde_json::to_string_pretty(&q).unwrap());
}
