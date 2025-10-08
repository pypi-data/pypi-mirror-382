macro_rules! bigkmer
{
    ($N: literal) =>{
        paste! {
            #[pyclass]
            #[derive(Clone)]
            pub struct [<BytesSerial $N>](pub [u8;8*($N/32 + 1)]);

            #[pymethods]
            impl [<BytesSerial $N>]{
                const VSIZE : usize = 8*($N/32 + 1);
                #[new]
                pub fn new(data: &Bound<'_, PyAny>) -> PyResult<Self> {
                    let slice : &[u8] = data.downcast::<PyBytes>()?.extract::<&[u8]>().unwrap();
                    if slice.len() != Self::VSIZE{
                        return Err(PyValueError::new_err(format!("Expecting {} size got {}", Self::VSIZE, slice.len())));
                    }
                    Ok(Self(slice.try_into().unwrap()))
                }

                fn __bytes__(slf: PyRef<Self>) -> PyResult<Bound<'_, PyBytes>>{
                    Ok(PyBytes::new(slf.py(), slf.0.as_slice()))
                }

                #[staticmethod]
                pub fn size() -> PyResult<usize> {
                    Ok($N)
                }
            }

            impl From<[<BytesSerial $N>]> for SimdDataStore<$N>
            {
                fn from(value: [<BytesSerial $N>]) -> Self {
                    unsafe {
                        let ptr = value.0.as_ptr() as *const u64;
                        let narray : [u64; $N/32 + 1]= std::slice::from_raw_parts(ptr, $N / 32 + 1).try_into().unwrap();
                        Self(Simd::from_array(narray))
                    }
                }
            }

            impl From<SimdDataStore<$N>> for [<BytesSerial $N>]
            {
                fn from(value: SimdDataStore<$N>) -> Self{
                    unsafe {
                        let ptr = value.0.as_array().as_ptr() as *const u8;
                        let narray = std::slice::from_raw_parts(ptr, 8*($N/32 + 1));
                        Self(narray.as_chunks_unchecked::<{ 8*($N/32 + 1)}>()[0])
                    }
                }
            }
            kmer!([<BytesSerial $N>], SimdDataStore<$N>, $N);
        }
    }
}

pub(crate) use bigkmer;
