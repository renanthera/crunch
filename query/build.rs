fn main() {
    cynic_codegen::register_schema("warcraftlogs")
        .from_sdl_file("schemas/warcraftlogs.schema")
        .unwrap()
        .as_default()
        .expect("failed to find GraphQL schema");
}
