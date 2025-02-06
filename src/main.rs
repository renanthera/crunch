use std::time::Instant;
use query::*;

fn wrap(f: fn() -> ()) {
    let a = Instant::now();
    f();
    let b = Instant::now();
    println!("{}", b.duration_since(a).as_nanos());
}

fn main() {
    let v = || {
        let a = RequestPoints::run_query(());
        println!("{:?}", a);
    };
    wrap(v);

    let w = || {
        let a = ReportFights::run_query(ReportFightsVariables {
            code: Some("GdY1kHybjFq8WgzR"),
        });
        println!("{:?}", a);
    };
    wrap(w);
}
