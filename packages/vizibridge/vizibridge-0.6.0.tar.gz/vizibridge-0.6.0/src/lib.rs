#![feature(generic_const_exprs)]
#![feature(portable_simd)]

//! This is the main entry point of the lib
//! We materialized all types that could be usefull
//! As we have 64 of them (32 for u64 type and 32 for u128)
//! we use seq! macro to generate all that in a concise way.
//!
//! To expose novel code, add a new module and integrate it belows.

#![allow(non_local_definitions)]
use crate::pydna::{PyDNA, PyNucleotid};
use crate::pyindex::*;
use crate::pykmer::*;
use paste::paste;
use pyo3::exceptions::{PyKeyError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyIterator, PyString, PyTuple, PyType};
use seq_macro::seq;
use std::env;
use std::path::Path;
use std::simd::Simd;
use vizitig_lib::iterators::{CanonicalKmerIterator, KmerIterator};
use vizitig_lib::kmer::Kmer;
use vizitig_lib::kmer_index::{IndexIterator, KmerIndex, KmerIndexEntry};
use vizitig_lib::kmer_simd::SimdDataStore;

pub mod pybigkmer;
pub mod pydna;
pub mod pyindex;
pub mod pykmer;
pub mod pykmer_index;
pub mod pyggcat;

macro_rules! build_kmer_index{
    ($N: expr, $store: expr) => {
        pykmer_index::PyKmerSet!($N, $store);
        pykmer_index::PyIndexIterator!($N, $store, {u8 u16 u32 u64 u128});
        pykmer_index::PyKmerIndex!($N, $store, u8,  {u64});
        pykmer_index::PyKmerIndex!($N, $store, u16, {u64});
        pykmer_index::PyKmerIndex!($N, $store, u32, {u64});
        pykmer_index::PyKmerIndex!($N, $store, u64, {u64});
        pykmer_index::PyKmerIndex!($N, $store, u128,{u64});
    }
}

macro_rules! bigkmer_index {
    ($N:expr) => {
        paste! {
            type [<Store $N>] = SimdDataStore<$N>;
            build_kmer_index!($N, [<Store $N>]);
        }
    };
}

macro_rules! add_kmer_extra {
    ($m:expr, $N: expr) => {
        paste! {
                    $m.add_class::<[<KmerSet $N>]>()?;
        //            $m.add_class::<[<KmerIndex $N u8>]>()?;
        //            $m.add_class::<[<KmerIndex $N u16>]>()?;
        //            $m.add_class::<[<KmerIndex $N u32>]>()?;
                    $m.add_class::<[<KmerIndex $N u64>]>()?;
        //            $m.add_class::<[<KmerIndex $N u128>]>()?;
                }
    };
}

macro_rules! all_bigkmer{
    ($m: expr, $($N:expr)*) => {
        paste!{
        $(
            pybigkmer::bigkmer!($N);
            bigkmer_index!($N);
            $m.add_class::<[< PyKmer $N>]>()?;
            $m.add_class::<[< BytesSerial $N >]>()?;
            add_kmer_extra!($m, $N);
        )*
        }
    }
}

macro_rules! smallkmer {
    ($m: expr,$t:ty, $N:expr) => {
        paste! {
            pykmer::kmer!($t, $t, $N);
            build_kmer_index!($N, $t);
            $m.add_class::<[< PyKmer $N>]>()?;
            add_kmer_extra!($m, $N);
        }
    };
}

#[cfg(feature = "few_kmer")]
fn base_kmer(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    smallkmer!(m, u64, 21);
    smallkmer!(m, u128, 55);
    all_bigkmer! {m, 97 2047};
    Ok(())
}

#[cfg(not(feature = "few_kmer"))]
fn base_kmer(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    seq!(N in 2..=31{
        smallkmer!(m, u64, N);
    });
    seq!(N in 33..=63{
        smallkmer!(m, u128, N);
    });
    all_bigkmer! {m, 113 127 239 241 251 255 487 491 499 509 511 1021 1023}
    Ok(())
}

#[inline(always)]
fn base_module(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {

    m.add_function(wrap_pyfunction!(pyggcat::build_graph, m)?)?;
    m.add_class::<pydna::PyDNA>()?;
    m.add_class::<pydna::PyNucleotid>()?;
    base_kmer(_py, m).unwrap();
    m.add_class::<pyindex::IntIndexu32u8>()?;
    m.add_class::<pyindex::IntIndexu32u32>()?;
    m.add_class::<pyindex::IntIndexu32u16>()?;
    m.add_class::<pyindex::IntIndexu32u128>()?;
    m.add_class::<pyindex::IntIndexu64u8>()?;
    m.add_class::<pyindex::IntIndexu64u32>()?;
    m.add_class::<pyindex::IntIndexu64u16>()?;
    m.add_class::<pyindex::IntIndexu64u128>()?;
    m.add_class::<pyindex::IntIndexu64u128>()?;
    m.add_class::<pyindex::IntIndexu128u8>()?;
    m.add_class::<pyindex::IntIndexu128u32>()?;
    m.add_class::<pyindex::IntIndexu128u16>()?;
    m.add_class::<pyindex::IntIndexu128u128>()?;
    m.add_class::<pyindex::IntIndexu128u128>()?;
    m.add_class::<pyindex::IntSetu128>()?;
    m.add_class::<pyindex::IntSetu64>()?;
    m.add_class::<pyindex::IntSetu32>()?;
    Ok(())
}

macro_rules! version {
    ($l: expr, $flag: literal) => {
        paste! {
            #[target_feature(enable = $flag)]
            unsafe fn [<_vizibridge_ $l>](_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
                base_module(_py, m)
            }
        }
    };
}

#[cfg(any(target_arch="x86_64"))]
#[pymodule]
fn _vizibridge(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {

    version!(avx512vl, "avx512vl");
    version!(avx2, "avx2");
    version!(sse3, "sse3");

    unsafe {
        if env::var("VIZIBRIDGE_AVX512_ENABLE").is_ok() && is_x86_feature_detected!("avx512vl") {
            if env::var("VIZIBRIDGE_INFO").is_ok() {
                println!("WARNING, using AVX512VL");
            }
            return _vizibridge_avx512vl(_py, m);
        }
        if env::var("VIZIBRIDGE_AVX2_DISABLE").is_err() && is_x86_feature_detected!("avx2") {
            if env::var("VIZIBRIDGE_INFO").is_ok() {
                println!("WARNING, using AVX2");
            }
            return _vizibridge_avx2(_py, m);
        }
        if env::var("VIZIBRIDGE_SSE3_DISABLE").is_err() && is_x86_feature_detected!("sse3") {
            if env::var("VIZIBRIDGE_INFO").is_ok() {
                println!("WARNING, using SSE");
            }
            return _vizibridge_sse3(_py, m);
        }
    }
    base_module(_py, m)
}

#[cfg(any(target_arch="aarch64"))]
#[pymodule]
fn _vizibridge(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    base_module(_py, m)
}
