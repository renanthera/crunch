use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;
use quote::quote;

#[proc_macro_attribute]
pub fn cache(attr: TokenStream, item: TokenStream) -> TokenStream {
    let input: syn::ItemStruct = match syn::parse(item) {
        Ok(is) => is,
        Err(err) => return syn::Error::from(err).to_compile_error().into(),
    };

    let contents: TokenStream2 = match syn::parse::<syn::LitBool>(attr) {
        Ok(is) => match is.value {
            true => quote!{
                crate::request::run_query_cached::<Self, U>(params)
            },
            false => quote!{
                crate::request::run_query_uncached::<Self, U>(params)
            }
        },
        Err(err) => return syn::Error::from(err).to_compile_error().into(),
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

// #[proc_macro_derive(Cache)]
// pub fn derive_cache(item: TokenStream) -> TokenStream {
//     let input = parse_macro_input!(item as DeriveInput);
//     let name = input.ident;
//     quote!{
//         #[automatically_derived]
//         impl crate::request::Cache for #name {}
//     }.into()
// }
