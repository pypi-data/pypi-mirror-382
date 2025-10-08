# Vizibridge

This module is a [maturin](https://www.maturin.rs/) bridge between the rust crate [vizicomp](https://gitlab.inria.fr/cpaperma/vizicomp)
containing compiled code for efficient genomic data manipulation in the Python module [Vizitig](https://gitlab.inria.fr/pydisk/examples/vizitig/)

## How to install vizibridge

The simplest way is to use `pip` as `vizibridge` is deploy in Pypi:

```bash
pip install vizibridge
```

Alternative, download the wheel from the [latest release obtained from gitlab](https://gitlab.inria.fr/cpaperma/vizibridge/-/releases/permalink/latest)

In the case where your architecture/systems is not presents, it is possible to compile it locally as well as follows.

First install the [rust tool chain](https://www.rust-lang.org) and then run 

```bash
cargo install maturin
maturin build --release
```

To install the module in your python then run

```bash
pip install target/wheels/vizibridge**.whl
``` 
replacing `**` by the appropriate name generated in the folder.


## Publication to pypi through CI/CD:

The CI/CD takes care to compiling everything so you can simply push the content to create a new compiled module.
To publish to Pypi, simply push a release tag:

```bash
git tag -d vx -m "Some description of the release to broadcast
git push origin vx 
``` 

Here `vx` is the version number that should be sync with the version declared in the `Cargo.toml`.

## Publication to pypi: 

First you must:

- Have docker installed
- A token to push vizibridge on pypi. 

Then from the main directory of vizibridge run:

```
docker build --build-arg PYPI_TOKEN="YOU_PYPI_TOKEN" .
```


## What should be here

The actual computing content should never been performed within this repo but
always either in `vizicomp` repo or through another repo that we would like to
have exposed in the Python ecosystem.  This repo is **solely** dedicated to
performing the bridge without polluting efficient standalone Rust tooling.


# Quick documentation of Python API

The Python Interface is composed of several component:

## Base type

### DNA type (`vizibridge.DNA`)

`DNA` is a Python class wrapper around `vizibrdge.rust_DNA` which is an encoding of DNA-string in rust. 
The underlying data-layout is simply using 2bits per nucleotid. The buildup of a DNA type from a string
is roughly 1 Gbyte/s.

Its main purpose is to provide a way to enumerate Kmer efficiently through `enum_kmer` and `enum_canonical_kmer`
methods. It can also be convert back to a string.

```python
from vizibridge import DNA
dna = DNA("ACGT"*10)
print(dna)
# display: ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT
print(repr(next(dna.enum_canonical_kmer(4))))
# display: 4-mer(ACGT)
```

### Kmer types (`vizibridge.Kmers`)

Two kind of type are defined in the rust code: ShortKmer and LongKmer.
ShortKmer encode Kmer on 64bits integers while LongKmer uses 128bit integer.
Each type came with its own compile code, so we have 64 different rust based
KmerType.

The Python module help with a class wrapper that provide a common interface:
`vizibridge.Kmer`. The building of a Kmer must go through `DNA` class.

```python
from vizibridge import Kmer, DNA
kmer = Kmer.from_DNA(DNA("ACGT")) # a 4-Kmer
print(repr(kmer))
# display: 4-mer(ACGT)
```

The underlying integer can be found in the `data` field which is used
to compute hash value for the Kmer. 

```python
print(kmer.data)
# display: 27 
```

Carefull, the hash is based uniquely on the integer content, so two kmer of distinct size
can have the same integer encoding and thus the same hash.

```python
kmer2 = Kmer.from_DNA(DNA("AAACGT"))
assert hash(kmer) == hash(kmer2)
```

Kmers can be convert to string, are hashable, and we can build another Kmer by appending left or right
nucleotid.

```python
print(repr(kmer))
# display: 4-mer(ACGT)
kmer3 = kmer.add_left_nucleotid('A')
print(repr(kmer3)
# display: 4-mer(AACG)
kmer4 = kmer3.add_left_nucleotid('A')
print(repr(kmer4)
# display: 4-mer(AAAG)
```

## Index types

Index are either: 
- KmerIndex: sorted arrays of pairs (Kmer, integer) where the integers are 32bits unsigned integers.
- KmerSet: sorted arrays of Kmer.

The filter out dupplicate, KmerSet have a *set* semantic and KmerIndex have a
*mapping* semantic.  They must be provided with a path toward a file for
storing the index. Underthehood, the index are simply sorted array and memory
map file. Carefull, memory map are not always portable (to check carefully on
Windows).

Two method exists to build an KmerIndex:

- build: take an iterate over a KmerIndexEntry (a dataclass with two field, kmer and value)
- build_dna: take an iterate over a DNAIndexEntry (a dataclass with two fields, dna and value).

The `build_dna` unfold each DNA-value into kmer through `enum_canonical_kmer` methods. It is more
efficient to use when you can associate all Kmer of a DNA sequence to one value. On the top of that,
`build_dna` take two integer to filter-out some kmer with respect to their value modulo something.
This is usefull when dispatching Kmer amongs several Shard.

Here a small example of usage.

```python
from vizibridge import DNA
some_kmer = list(DNA("ACGT").enum_canonical_kmer(2))
d = { kmer: i for i, kmer in enumerate(some_kmer) }
print(d)
# display: {2-mer(AC): 2, 2-mer(CG): 1}
# We have only two kmer because AC occurs twice, in position 0 and 2

from vizibridge import KmerIndex, KmerIndexEntry
from pathlib import Path
index = KmerIndex.build((KmerIndexEntry(kmer=k, val=i) for i,k in enumerate(some_kmer)), Path("/tmp/some_path"), 2) # 2 is the kmer-size
print(index[some_kmer[1]])
# display: 1

print(dict(index))
# display: {2-mer(AC): 2, 2-mer(CG): 1}
```

KmerSet follows the same principle, except it have a Set semantic (hence no value associated to Kmer)

```python
s = set(some_kmer)
print(s)
# display: {2-mer(AC), 2-mer(CG)}

from vizibridge import KmerSet
from pathlib import Path
index = KmerSet.build(iter(some_kmer), Path("/tmp/some_other_path"), 2) # 2 is the kmer-size
print(some_kmer[1] in index)
# display: True

print(set(index))
# display: {2-mer(AC), 2-mer(CG)}
```

# TODO

- Add in the CI/CD windows and MacOS compilations
- Integrate ggcat binding
- Other tools?
