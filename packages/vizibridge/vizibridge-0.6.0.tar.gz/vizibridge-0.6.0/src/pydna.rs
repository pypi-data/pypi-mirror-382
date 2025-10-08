//use crate::pykmer::*;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyString, PyType};
use vizitig_lib::dna::{Nucleotid, DNA};

#[pyclass]
#[derive(Clone)]
pub struct PyNucleotid(pub Nucleotid);

#[pymethods]
impl PyNucleotid {
    #[classmethod]
    fn from_char(_: &Bound<'_, PyType>, input: &Bound<'_, PyString>) -> PyResult<Self> {
        let input_str = input.to_str()?;
        match input_str.len() {
            1 => Ok(Self(input_str.chars().next().unwrap().try_into().unwrap())),
            _ => Err(PyValueError::new_err("Input str is not a char (len>1)")),
        }
    }

    #[classmethod]
    fn from_u8(_: &Bound<'_, PyType>, input: u8) -> PyResult<Self> {
        Ok(Self(input.try_into().unwrap()))
    }

    fn __str__(&self) -> PyResult<String> {
        Ok(format!("{}", self.0))
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("Nucleotid<{}>", self.0))
    }

    fn complement(&self) -> PyResult<Self> {
        Ok(Self(self.0.complement()))
    }

    fn __add__(&self, other: &Bound<'_, PyAny>) -> PyResult<PyDNA> {
        let n1: Nucleotid = self.0;
        let n2: Nucleotid = other.extract::<Self>()?.0;
        Ok(PyDNA(DNA(vec![n1, n2])))
    }
}

/// A class wrapper around a DNA struct from vizicomp
#[pyclass]
#[derive(Clone)]
pub struct PyDNA(pub DNA);

#[pymethods]
impl PyDNA {
    #[new]
    pub fn new(input_pystr: &Bound<'_, PyString>) -> PyResult<Self> {
        let input_str = input_pystr.to_str()?;
        let dna = input_str.as_bytes().try_into().unwrap();
        Ok(PyDNA(dna))
    }

    pub fn __repr__(&self) -> PyResult<String> {
        Ok(format!("RustDNA<{}>", self.__str__().unwrap()))
    }

    pub fn __str__(&self) -> PyResult<String> {
        let repr: String = self.0 .0.clone().into_iter().map(char::from).collect();
        Ok(repr)
    }

    fn __len__(&self) -> PyResult<usize> {
        Ok(self.0 .0.len())
    }

    /// get the Nucleotid as a char at a given index
    pub fn get_index(&self, index: usize) -> PyResult<PyNucleotid> {
        Ok(PyNucleotid(self.0 .0[index]))
    }

    /// get a slice of the DNA
    pub fn get_slice(&self, start: usize, stop: usize) -> PyResult<Self> {
        Ok(PyDNA(DNA(self.0 .0.get(start..stop).unwrap().to_vec())))
    }
}
