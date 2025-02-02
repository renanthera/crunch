use warcraftlogs::query::ReportFightsVariables;
use warcraftlogs::request::Cache;

fn main() {
    // let v = warcraftlogs::query::RequestPoints::run_query(());
    // println!("{:?}", v);

    let w = warcraftlogs::query::ReportFights::run_query(ReportFightsVariables {
        code: Some("GdY1kHybjFq8WgzR"),
    });
    println!("{:?}", w);
}
