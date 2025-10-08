use pyo3::exceptions::PyTypeError;
use pyo3::prelude::*;
use vizitig_lib::kmer::{DataStore, Kmer};

#[derive(Clone, Copy)]
pub struct PyKmer<const N: usize, T: DataStore<N> + Ord>(pub Kmer<N, T>);

impl<const N: usize, T: DataStore<N> + Ord> From<Kmer<N, T>> for PyKmer<N, T> {
    fn from(value: Kmer<N, T>) -> Self {
        Self(value)
    }
}

impl<const N: usize, T: DataStore<N> + Ord> From<PyKmer<N, T>> for Kmer<N, T> {
    fn from(value: PyKmer<N, T>) -> Self {
        value.0
    }
}

impl<'py, const N: usize, T> FromPyObject<'py> for PyKmer<N, T>
where
    T: DataStore<N> + Ord + FromPyObject<'py>,
{
    #[inline(always)]
    fn extract_bound(input: &Bound<'py, PyAny>) -> PyResult<Self> {
        let data: T = input.extract()?;
        Ok(Self(Kmer::<N, T>(data)))
    }
}

impl<'py, const N: usize, T> IntoPyObject<'py> for PyKmer<N, T>
where
    T: DataStore<N> + Ord + IntoPyObject<'py, Output = Bound<'py, PyAny>>,
{
    type Target = PyAny;
    type Output = Bound<'py, Self::Target>;
    type Error = PyErr;

    #[inline(always)]
    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        match self.0 .0.into_pyobject(py) {
            Ok(val) => Ok(val),
            Err(_) => Err(PyTypeError::new_err("Conversion error")),
        }
    }
}

macro_rules! kmer {
    ($serial: ty, $store:ty, $N: literal) => {
        paste!
        {
            #[pyclass]
            #[derive(Clone)]
            pub struct [<PyKmer $N>](pub PyKmer<$N, $store>);

            #[pymethods]
            impl [<PyKmer $N>]{
                #[new]
                pub fn new(data: $serial) -> PyResult<Self> {
                    Ok(Self(PyKmer::<$N, $store>(Kmer::<$N, $store>(data.into()))))
                }

                #[classmethod]
                pub fn enumerate_canonical_kmer(_: &Bound<'_, PyType>, dna: PyDNA) -> PyResult<Vec<Self>>
                {
                    let it : CanonicalKmerIterator<$N, $store> = (&(dna.0)).try_into().unwrap();
                    Ok(it.map(|u| Self(u.into())).collect())
                }

                #[classmethod]
                pub fn from_str(_: &Bound<'_, PyType>, base_str: &Bound<'_, PyString>) -> PyResult<Self>
                {
                    let input_str = base_str.to_str()?;
                    Ok(Self(PyKmer::<$N, $store>(input_str.try_into().unwrap())))
                }

                #[classmethod]
                pub fn from_dna(_: &Bound<'_, PyType>, base_dna: PyDNA) -> PyResult<Self>
                {
                    Ok(Self(PyKmer::<$N, $store>(base_dna.0.0.first_chunk::<$N>().unwrap().into())))
                }

                #[classmethod]
                pub fn enumerate_kmer(_: &Bound<'_, PyType>, dna: PyDNA) -> PyResult<Vec<Self>>
                {
                    let it : KmerIterator<$N, $store> = (&(dna.0)).try_into().unwrap();
                    Ok(it.map(|u| Self(u.into())).collect())
                }

                #[staticmethod]
                pub fn size() -> PyResult<usize> {
                    Ok($N)
                }

                pub fn add_left_nucleotid(&self, n: PyNucleotid) -> PyResult<Self>{
                    Ok(Self(self.0.0.append_left(n.0).into()))
                }

                pub fn add_right_nucleotid(&self, n: PyNucleotid) -> PyResult<Self>{
                    Ok(Self(self.0.0.append(n.0).into()))
                }

                pub fn reverse_complement(&self) -> PyResult<Self>{
                    Ok(Self(self.0.0.rc().into()))
                }

                pub fn canonical(&self) -> PyResult<Self>{
                    Ok(Self(self.0.0.normalize().into()))
                }

                pub fn is_canonical(&self) -> PyResult<bool>{
                    Ok(self.0.0 == self.0.0.normalize())
                }

                #[getter]
                pub fn data(&self) -> PyResult<$serial>{
                    Ok(self.0.0.get_data().into())
                }

                pub fn __hash__(&self) -> PyResult<i64>{
                    Ok(self.0.0.hash())
                }

                pub fn __repr__(&self) -> PyResult<String>{
                    Ok(format!("{}", &self.0.0))
                }

                pub fn __str__(&self) -> PyResult<String>{
                    Ok((&self.0.0).into())
                }

                pub fn __lt__(&self, other: Self) -> PyResult<bool> {
                    Ok(self.0.0 <= other.0.0)
                }

                pub fn __gt__(&self, other: Self) -> PyResult<bool> {
                    Ok(self.0.0 >= other.0.0)
                }

                pub fn __eq__(&self, other: Self) -> PyResult<bool> {
                    Ok(self.0.0 == other.0.0)
                }
            }
        }
    }
}

pub(crate) use kmer;
