use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;
use quote::quote;
use syn::{parse, Error, ItemStruct, LitBool};

// TODO: can the `run_query` boilerplate be extracted from the extant impls,
// to avoid needing to update it here as well if it changes?

// combines all relevant derives and switches the `run_query` impl based on
// whether the query struct requests caching to be enabled
#[proc_macro_attribute]
pub fn cache(attr: TokenStream, item: TokenStream) -> TokenStream {
    let input: ItemStruct = match parse(item) {
        Ok(is) => is,
        Err(err) => return Error::from(err).to_compile_error().into(),
    };

    let contents: TokenStream2 = match parse::<LitBool>(attr) {
        Ok(is) => match is.value {
            true => quote! {
                run_query_cached::<Self, U>(params)
            },
            false => quote! {
                run_query_uncached::<Self, U>(params)
            },
        },
        Err(err) => return Error::from(err).to_compile_error().into(),
    };

    let name = &input.ident;

    quote! {
        #[derive(cynic::QueryFragment, Debug, serde::Serialize)]
        #[serde(rename_all = "camelCase")]
        #input

        impl warcraftlogs::request::Cache for #name {
            fn run_query<U>(params: U) -> Result<Self, warcraftlogs::error::Error>
            where
                U: cynic::QueryVariables + serde::Serialize,
                Self: Sized + cynic::QueryBuilder<U> + serde::Serialize + for<'a> serde::Deserialize<'a> + 'static
            {
                use warcraftlogs::request::{run_query_cached, run_query_uncached};
                #contents
            }
        }
    }
    .into()
}
