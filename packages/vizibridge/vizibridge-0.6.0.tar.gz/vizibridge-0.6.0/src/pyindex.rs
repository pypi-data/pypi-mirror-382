use paste::paste;
use pyo3::exceptions::PyKeyError;
use pyo3::prelude::*;
use pyo3::types::{PyIterator, PyString, PyType};
use std::path::Path;
use vizitig_lib::kmer_index::{Index, IndexEntry, IndexIterator};

macro_rules! IntIndex
{
    ($typl: expr, $typr: expr) =>
    {
        paste!
        {

            #[pyclass]
            pub struct [<IndexIterator $typl $typr>](IndexIterator<$typl, $typr>);

            #[pymethods]
            impl [<IndexIterator $typl $typr>]{
                fn __iter__(slf: PyRef<Self>) -> PyRef<Self> {
                    slf
                }

                fn __next__(mut slf: PyRefMut<Self>) -> Option<($typl, $typr)> {
                    match slf.0.next() {
                        Some(index_entry) => Some((index_entry.key, index_entry.val.try_into().unwrap())),
                        _ => None,
                    }
                }
            }

            #[pyclass]
            #[derive(Clone)]
            pub struct [<IntIndex $typl $typr>](pub Index<$typl, $typr>);

            #[pymethods]
            impl [<IntIndex $typl $typr>]{
                #[classmethod]
                pub fn build(
                    _: &Bound<'_, PyType>,
                    iterator: &Bound<'_, PyIterator>,
                    index_path: &Bound<'_, PyString>,
                    buffer_size: usize,
                ) -> PyResult<Self> {
                    let path: &Path = Path::new(index_path.to_str()?);
                    let entry_iter = iterator.try_iter()?.map(|i| {
                        i.and_then(|i| {
                            Ok(IndexEntry::<$typl, $typr> {
                                key: i.getattr("key")?.extract::<$typl>().unwrap(),
                                val: i.getattr("val")?.extract::<$typr>().unwrap(),
                            })
                        })
                    });

                    Ok(Self(Index::<$typl, $typr>::build_index(
                            entry_iter.map(|e| e.unwrap()),
                            path,
                            buffer_size,
                        )
                        .unwrap()
                    ))
                }

                pub fn __len__(&self) -> PyResult<usize> {
                    Ok(self.0.len())
                }

                pub fn __getitem__(&self, key: $typl) -> PyResult<$typr> {
                    match self.0.get(key) {
                        Ok(val) => Ok(val),
                        _ => Err(PyKeyError::new_err(key)),
                    }
                }

                #[new]
                fn new(index_path: &Bound<'_, PyString>) -> PyResult<Self> {
                    let path: &Path = Path::new(index_path.to_str()?);
                    Ok(Self(Index::<$typl, $typr>::load_index(path).unwrap()))
                }

                fn __iter__(slf: PyRef<Self>) -> PyResult<Py<[<IndexIterator $typl $typr>]>> {
                    let iter = [<IndexIterator $typl $typr>](slf.0.clone().into_iter());
                    Py::new(slf.py(), iter)
                }
            }
        }
    }
}

macro_rules! IntSetIndex
{
    ($typ: expr) => {
        paste!{
                #[pyclass]
                pub struct [<IndexIteratorSet $typ>](pub IndexIterator<$typ, ()>);

                #[pymethods]
                impl [<IndexIteratorSet $typ>] {
                    fn __iter__(slf: PyRef<Self>) -> PyRef<Self> {
                        slf
                    }

                    fn __next__(mut slf: PyRefMut<Self>) -> Option<$typ> {
                        match slf.0.next() {
                            Some(index_entry) => Some(index_entry.key),
                            _ => None,
                        }
                    }
                }

                #[pyclass]
                #[derive(Clone)]
                pub struct [<IntSet $typ>](pub Index<$typ, ()>);

                #[pymethods]
            impl [<IntSet $typ>]{

                #[classmethod]
                pub fn build(
                    _: &Bound<'_, PyType>,
                    iterator: &Bound<'_, PyIterator>,
                    index_path: &Bound<'_, PyString>,
                    buffer_size: usize,
                ) -> PyResult<Self> {
                    let path: &Path = Path::new(index_path.to_str()?);
                    let entry_iter = iterator.try_iter()?.map(|i| {
                        i.and_then(|i| {
                            Ok(IndexEntry::<$typ, ()> {
                                key: i.getattr("key")?.extract::<$typ>().unwrap(),
                                val: (),
                            })
                        })
                    });

                    Ok(Self(
                        Index::<$typ, ()>::build_index(entry_iter.map(|e| e.unwrap()), path, buffer_size)
                            .unwrap(),
                    ))
                }

                pub fn __len__(&self) -> PyResult<usize> {
                    Ok(self.0.len())
                }

                pub fn __getitem__(&self, key: $typ) -> PyResult<()> {
                    match self.0.get(key) {
                        Ok(val) => Ok(val),
                        _ => Err(PyKeyError::new_err(key)),
                    }
                }

                pub fn __contains__(&self, key: $typ) -> PyResult<bool> {
                    match self.0.get(key) {
                        Ok(_) => Ok(true),
                        _ => Ok(false),
                    }
                }

                #[new]
                fn new(index_path: &Bound<'_, PyString>) -> PyResult<Self> {
                    let path: &Path = Path::new(index_path.to_str()?);
                    Ok(Self(
                        Index::<$typ, ()>::load_index(path).unwrap(),
                    ))
                }

                fn __iter__(slf: PyRef<Self>) -> PyResult<Py<[<IndexIteratorSet $typ>]>> {
                    let iter = [<IndexIteratorSet $typ>](slf.0.clone().into_iter());
                    Py::new(slf.py(), iter)
                }
            }
        }
    }
}

macro_rules! gen_all_index
{
    ($($typ: expr)*)=> {
        $(
        IntIndex!($typ, u8);
        IntIndex!($typ, u16);
        IntIndex!($typ, u32);
        IntIndex!($typ, u64);
        IntIndex!($typ, u128);
        IntSetIndex!($typ);
        )*
    }
}

gen_all_index!(u8 u16 u32 u64 u128);
