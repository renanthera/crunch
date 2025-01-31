use warcraftlogs::query;

fn main() {
    let v = warcraftlogs::run_query!(query::RequestPoints);
    println!("{:?}", v);
}
