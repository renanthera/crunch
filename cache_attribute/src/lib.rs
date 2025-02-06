use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;
use quote::quote;
use syn::{parse, Error, ItemStruct, LitBool};

// TODO: solve pagination :(

// combines all relevant derives and switches the `run_query` impl based on whether the query struct requests caching to be enabled
#[proc_macro_attribute]
pub fn cache(attr: TokenStream, item: TokenStream) -> TokenStream {
    let input: ItemStruct = match parse(item) {
        Ok(is) => is,
        Err(err) => return Error::from(err).to_compile_error().into(),
    };

    let contents: TokenStream2 = match parse::<LitBool>(attr) {
        Ok(is) => match is.value {
            true => quote! {
                crate::request::run_query_cached::<Self, U>(params)
            },
            false => quote! {
                crate::request::run_query_uncached::<Self, U>(params)
            },
        },
        Err(err) => return Error::from(err).to_compile_error().into(),
    };

    let name = &input.ident;

    quote! {
        #[derive(cynic::QueryFragment, Debug, serde::Serialize)]
        #[serde(rename_all = "camelCase")]
        #input

        impl crate::request::Cache for #name {
            fn run_query<U>(params: U) -> Result<Self, Error>
            where
                U: cynic::QueryVariables + serde::Serialize,
                Self: Sized + cynic::QueryBuilder<U> + serde::Serialize + for<'a> serde::Deserialize<'a> + 'static
            {
                #contents
            }
        }
    }
    .into()
}
