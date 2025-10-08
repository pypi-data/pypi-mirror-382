macro_rules! PyKmerIndex
{
    ($N: expr, $store: expr, $typ: expr, { $($typr: expr)* }) =>
    {
        paste!
        {
            #[pyclass]
            #[derive(Clone)]
            pub struct [<KmerIndex $N $typ>](pub KmerIndex<$N, $store, $typ>);

            #[pymethods]
            impl [<KmerIndex $N $typ>]{
                #[classmethod]
                pub fn build(_: &Bound<'_, PyType>, iterator: &Bound<'_, PyIterator>, index_path: &Bound<'_, PyString>, buffer_size: usize) -> PyResult<Self> {
                    let path : &Path = Path::new(index_path.to_str()?);
                    let kmer_entry_iter = iterator.try_iter()?.map(|i| i.and_then(|i|{
                        let base_tuple = i.downcast::<PyTuple>().unwrap();
                        let kmer : [<PyKmer $N>] = base_tuple.get_item(0)?.extract().unwrap();
                        let val : $typ = base_tuple.get_item(1)?.extract().unwrap();
                        Ok(KmerIndexEntry::<$N, $store, $typ>{
                            key: kmer.0.into(),
                            val
                        })
                        }));

                    Ok(Self(
                         KmerIndex::<$N, $store, $typ>::build_index(kmer_entry_iter.map(|e| e.unwrap()), path, buffer_size).unwrap(),
                    ))
                }

                /// Build the shard by keeping only kmer satisfying (kmer.hash() % modulo == index)
                #[classmethod]
                pub fn build_dna(_: &Bound<'_, PyType>,
                                iterator: &Bound<'_, PyIterator>,
                                index_path: &Bound<'_, PyString>,
                                buffer_size: usize, index: i64, modulo: i64
                ) -> PyResult<Self> {
                    let path : &Path = Path::new(index_path.to_str()?);
                    let dna_entry_iter = iterator.try_iter()?.map(|i| i.and_then(|i|{
                        let base_tuple = i.downcast::<PyTuple>().unwrap();
                        let dna : PyDNA = base_tuple.get_item(0)?.extract().unwrap();
                        let val : $typ = base_tuple.get_item(1)?.extract().unwrap();
                        Ok((dna, val))
                    }));
                    let kmer_iter = dna_entry_iter.map(|e| e.unwrap()).flat_map(|(dna, val)|{
                        let kmer_it : CanonicalKmerIterator<$N, $store> = (&dna.0).into();
                        let kmer_vec: Vec<KmerIndexEntry::<$N, $store, $typ>> =
                                        kmer_it.filter(|kmer| kmer.hash().rem_euclid(modulo) == index)
                                        .map(move |kmer| KmerIndexEntry::<$N, $store, $typ>{
                                            key: kmer,
                                            val
                                        }).collect();
                        kmer_vec.into_iter()
                        });
                    Ok(Self(
                        KmerIndex::<$N, $store, $typ>::build_index(kmer_iter, path, buffer_size).unwrap(),
                    ))
                }

                /// Build the shard by keeping only kmer satisfying (kmer.hash() % modulo == index)
                /// the second component stored is incremented for each_kmer like an enumerate
                /// construct.
                #[classmethod]
                pub fn build_dna_enumerate(_: &Bound<'_, PyType>,
                                iterator: &Bound<'_, PyIterator>,
                                index_path: &Bound<'_, PyString>,
                                buffer_size: usize, index: i64, modulo: i64
                ) -> PyResult<Self> {
                    let path : &Path = Path::new(index_path.to_str()?);
                    let dna_entry_iter = iterator.try_iter()?.map(|i| i.and_then(|i|{
                        let base_tuple = i.downcast::<PyTuple>().unwrap();
                        let dna : PyDNA = base_tuple.get_item(0)?.extract().unwrap();
                        let val : $typ = base_tuple.get_item(1)?.extract().unwrap();
                        Ok((dna, val))
                    }));
                    let kmer_iter = dna_entry_iter.map(|e| e.unwrap()).flat_map(|(dna, val)|{
                        let mut offset = val;
                        let kmer_it : CanonicalKmerIterator<$N, $store> = (&dna.0).into();
                        let mut kmer_vec: Vec<KmerIndexEntry::<$N, $store, $typ>> = vec![];
                        for kmer in kmer_it {
                            if kmer.hash().rem_euclid(modulo) == index{
                                kmer_vec.push( KmerIndexEntry::<$N, $store, $typ>{
                                    key:kmer,
                                    val: offset,
                                });
                            }
                            offset += 1;
                        }
                        kmer_vec.into_iter()
                        });
                    Ok(Self(
                        KmerIndex::<$N, $store, $typ>::build_index(kmer_iter, path, buffer_size).unwrap(),
                    ))
                }


                pub fn intersection_index(&self,
                    other: &[<KmerSet $N>],
                    out_path: &Bound<'_, PyString>,
                    buffer_size: usize) -> PyResult<[<IntSet $typ>]>{

                    let path: &Path = Path::new(out_path.to_str().unwrap());
                    Ok([<IntSet $typ>](
                        self.0.join_index::<()>(other.0.clone(), path, buffer_size)
                    ))
                }


                pub fn intersection_iter(&self,
                        iterator: &Bound<'_, PyIterator>,
                        out_path: &Bound<'_, PyString>,
                        buffer_size: usize
                ) -> PyResult<[<IntSet $typ>]>{
                    let path: &Path = Path::new(out_path.to_str().unwrap());
                    let parsed_iterator = iterator.try_iter()?.map(|i| i.and_then(|i|{
                        Ok((
                            i.extract::<[<PyKmer $N>]>().unwrap().0.into(),
                            ()
                        ))
                       })).map(|e| e.unwrap());
                    Ok(
                       [<IntSet $typ>](
                            self.0.join_iter(parsed_iterator, path, buffer_size)
                        )
                    )
                }

                pub fn get_all(&self, kmer: [<PyKmer $N>]) -> PyResult<Vec<$typ>>{
                    match self.0.get_all(kmer.0.into()) {
                        Ok(iter)=> Ok(iter.collect()),
                        _ => Err(PyKeyError::new_err(kmer))
                    }
                }


                pub fn __len__(&self) -> PyResult<usize>{
                    Ok(self.0.len())
                }

                pub fn __getitem__(&self, kmer: [<PyKmer $N>]) -> PyResult<$typ>{
                    match self.0.get(kmer.0.into()) {
                        Ok(val) => Ok(val),
                        _ => Err(PyKeyError::new_err(kmer))
                    }
                }

                pub fn get_from_dnas(&self, iterator: &Bound<'_, PyIterator>) -> PyResult<Vec<([<PyKmer $N>], $typ)>> {
                    let dnas : Vec<_> = iterator.try_iter()?.map(|u|
                        u.and_then(|d| Ok(d.extract::<PyDNA>().unwrap().0))
                    ).map(|e| e.unwrap()).collect();
                    Ok(self.0.get_from_dnas(dnas).into_iter().map(|entry| 
                            ([<PyKmer $N>](entry.key.into()), entry.val)
                    ).collect())
                }

                #[new]
                fn new(index_path: &Bound<'_, PyString>) -> PyResult<Self>{
                    let path : &Path = Path::new(index_path.to_str()?);
                    Ok(Self(
                        KmerIndex::<$N, $store, $typ>::load_index(path).unwrap()
                    ))
                }


                fn __iter__(slf: PyRef<Self>) -> PyResult<Py<[<IndexIterator $N $typ>]>> {
                    let iter = [< IndexIterator $N $typ>](slf.0.clone().into_iter());
                    Py::new(slf.py(), iter)
                }

                #[staticmethod]
                fn size() -> PyResult<usize> {
                    Ok($N)
                }
                #[staticmethod]
                fn val_type() -> PyResult<usize> {
                    Ok(8*size_of::<$typ>())
                }

                $(
                pub fn [<join_iter $typr>](&self,
                        iterator: &Bound<'_, PyIterator>,
                        out_path: &Bound<'_, PyString>,
                        buffer_size: usize
                ) -> PyResult<[<IntIndex $typ $typr>]>{
                    let path: &Path = Path::new(out_path.to_str().unwrap());
                    let parsed_iterator = iterator.try_iter()?.map(|i| i.and_then(|i|{
                        let base_tuple = i.downcast::<PyTuple>().unwrap();
                        Ok((base_tuple.get_item(0)?.extract::<[<PyKmer $N>]>().unwrap().0.into(),
                            base_tuple.get_item(1)?.extract::<$typr>().unwrap())
                       )
                    })).map(|e| e.unwrap());
                    Ok(
                        [<IntIndex $typ $typr>](self.0.join_iter(parsed_iterator, path, buffer_size))
                    )
                }

                pub fn extract_uniq(&self, 
                    out_path: &Bound<'_, PyString>,
                    buffer_size: usize) -> PyResult<Self>{
                    let path: &Path = Path::new(out_path.to_str().unwrap());
                    Ok(Self(self.0.extract_uniq(path, buffer_size)))
                }

                pub fn [<join_index $typr>](&self,
                    other: &[<KmerIndex $N $typr>],
                    out_path: &Bound<'_, PyString>,
                    buffer_size: usize) -> PyResult<[<IntIndex $typ $typr>]>{

                    let path: &Path = Path::new(out_path.to_str().unwrap());
                    Ok([<IntIndex $typ $typr>](
                        self.0.join_index::<$typr>(other.0.clone(), path, buffer_size)
                    ))
                }
                )*


            }
        }
    }
}
macro_rules! PyIndexIterator
{
    ($N: expr, $store: expr,{ $($typ: expr)* }) =>
    {
        paste!{

            $(
            #[pyclass]
            pub struct [<IndexIterator $N $typ>](
                IndexIterator<Kmer<$N, $store>, $typ>
            );


            #[pymethods]
            impl [<IndexIterator $N $typ>] {
                fn __iter__(slf: PyRef<Self>) -> PyRef<Self> {
                    slf
                }

                fn __next__(mut slf: PyRefMut<Self>) -> Option<([<PyKmer $N>], $typ)>{
                    match slf.0.next(){
                        Some(index_entry) => Some(([<PyKmer $N>](index_entry.key.into()), index_entry.val)),
                        _ => None
                    }
                }
            }
            )*
        }
    }
}

macro_rules! PyKmerSet
{
    ($N: expr, $store: expr) =>
    {
        paste!{
            #[pyclass]
            #[derive(Clone)]
            pub struct [<KmerSet $N>](KmerIndex<$N, $store, ()>);

            #[pymethods]
            impl [<KmerSet $N>]{
                #[classmethod]
                pub fn build(_: &Bound<'_, PyType>, iterator: &Bound<'_, PyIterator>, index_path: &Bound<'_, PyString>, buffer_size: usize) -> PyResult<Self> {
                    let path : &Path = Path::new(index_path.to_str()?);
                    let kmer_entry_iter = iterator.try_iter()?.map(|i| i.and_then(|i|{
                        let kmer = i.extract::<[<PyKmer $N>]>().unwrap().0;
                        Ok(KmerIndexEntry::<$N, $store, ()>{
                            key: kmer.into(),
                            val: ()
                        })
                        }));

                    Ok(Self(
                        KmerIndex::<$N, $store, ()>::build_index(kmer_entry_iter.map(|e| e.unwrap()), path, buffer_size).unwrap(),
                    ))
                }

                #[classmethod]
                pub fn build_dna(_: &Bound<'_, PyType>, iterator: &Bound<'_, PyIterator>, index_path: &Bound<'_, PyString>, buffer_size: usize, index: i64, modulo: i64) -> PyResult<Self> {
                    let path : &Path = Path::new(index_path.to_str()?);
                    let dna_entry_iter = iterator.try_iter()?.map(|i| i.and_then(|i|{
                        let dna = i.extract::<PyDNA>().unwrap().0;
                        Ok(dna)
                    }));
                    let kmer_iter = dna_entry_iter.map(|e| e.unwrap()).flat_map(|dna|{
                        let kmer_it : CanonicalKmerIterator<$N, $store> = (&dna).into();
                        let kmer_it_filt = kmer_it.filter(|kmer| kmer.hash().rem_euclid(modulo) == index)
                                .map(move |kmer| KmerIndexEntry::<$N, $store, ()>{
                                    key: kmer,
                                    val: ()
                                });
                        let kmer_vec : Vec<KmerIndexEntry<$N, $store, ()>> = kmer_it_filt.collect();
                        kmer_vec.into_iter()
                    });
                    Ok(Self(
                        KmerIndex::<$N, $store, ()>::build_index(kmer_iter, path, buffer_size).unwrap(),
                    ))
                }
                pub fn __len__(&self) -> PyResult<usize>{
                    Ok(self.0.len())
                }

                pub fn __contains__(&self, kmer: [<PyKmer $N>]) -> PyResult<bool>{
                    match self.0.get(kmer.0.into()){
                        Ok(_) => Ok(true),
                        _ => Ok(false)
                    }
                }

                #[new]
                fn new(index_path: &Bound<'_, PyString>) -> PyResult<Self>{
                    let path : &Path = Path::new(index_path.to_str()?);
                    Ok(Self(
                        KmerIndex::<$N, $store, ()>::load_index(path).unwrap()
                    ))
                }


                fn __iter__(slf: PyRef<Self>) -> PyResult<Py<[<IndexSetIterator $N $store>]>> {
                    let iter = [<IndexSetIterator $N $store>](slf.0.clone().into_iter());
                    Py::new(slf.py(), iter)
                }

                #[staticmethod]
                fn size() -> PyResult<usize> {
                    Ok($N)
                }

            }

            #[pyclass]
            pub struct [<IndexSetIterator $N $store>](IndexIterator<Kmer<$N, $store>, ()>);

            #[pymethods]
            impl [<IndexSetIterator $N $store>] {
                fn __iter__(slf: PyRef<Self>) -> PyRef<Self> {
                    slf
                }

                fn __next__(mut slf: PyRefMut<Self>) -> Option<[<PyKmer $N>]> {
                    match slf.0.next(){
                        Some(index_entry) =>
                            Some([<PyKmer $N>](index_entry.key.into())),
                        _ => None
                    }
                }
            }
        }
    }
}

pub(crate) use PyIndexIterator;
pub(crate) use PyKmerIndex;
pub(crate) use PyKmerSet;
