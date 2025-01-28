mod cache;
mod query;
mod request;
mod token;

// #[derive(Debug, serde::Serialize, serde::Deserialize)]
// struct Temp {
//     body: String,
// }

fn main() {
    // let body = Temp {
    //     body: "12345asdfjkl".to_string(),
    // };

    // // let i = cache::insert("asdf".to_string(), &body).unwrap();
    // let s = cache::select::<Temp>("asdf".to_string()).unwrap();

    // match cache::select::<Temp>("asdf".to_string()) {
    //     Ok(ok) => println!("{:?}", ok),
    //     Err(ref err) => match err {
    //         cache::Error::NoResponse(..) => todo!(),
    //         _ => panic!("{}", err),
    //     }
    // }

    // // println!("{:?}", i);
    // println!("{:?}", s);
}
