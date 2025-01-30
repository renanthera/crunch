mod cache;
mod error;
mod query;
mod request;
mod token;

// TODO: split into subcrates
// - request, query, analysis

fn main() {
    let v = request::run_query!(query::RequestPoints);
    println!("{:?}", v);
}
