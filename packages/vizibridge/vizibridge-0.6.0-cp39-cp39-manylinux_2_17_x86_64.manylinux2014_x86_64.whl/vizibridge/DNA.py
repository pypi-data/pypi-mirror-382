from vizibridge._vizibridge import PyDNA as RustDNA, PyNucleotid as RustNucleotid
from vizibridge.kmers import Kmer, KmerTypeMap
from typing import Iterator
from typing_extensions import Self
import re

non_CGTA = re.compile("[^ACGT]")


class DNA:
    __slots__ = ("data",)

    def __init__(self, data: RustDNA | str):
        if isinstance(data, str):
            self.data = RustDNA(data)
        elif isinstance(data, RustDNA):
            self.data = data
        else:
            raise TypeError(type(data))

    @classmethod
    def from_str(cls, seq: str) -> Iterator[Self]:
        yield from (cls(subseq) for subseq in non_CGTA.split(seq))

    def __iter__(self) -> Iterator[RustNucleotid]:
        for i in range(len(self.data)):
            yield self.data.get_index(i)

    def __getitem__(self, __key: int | slice) -> Self | RustNucleotid:
        if isinstance(__key, int):
            return self.data.get_index(__key)
        if isinstance(__key, slice):
            assert __key.step is None
            data = self.data.get_slice(__key.start, __key.stop)
            return type(self)(data)

        raise KeyError(__key)

    def __repr__(self):
        return repr(self.data)

    def __str__(self):
        return str(self.data)

    def __len__(self):
        return len(self.data)

    def enum_canonical_kmer(self, k: int) -> Iterator[Kmer]:
        if k not in KmerTypeMap:
            raise NotImplementedError(
                f"{k=} is not valid. Chose in {str(set(KmerTypeMap))}"
            )
        return map(
            lambda e: Kmer(e, k), KmerTypeMap[k].enumerate_canonical_kmer(self.data)
        )

    def enum_kmer(self, k: int) -> Iterator[Kmer]:
        if k not in KmerTypeMap:
            raise NotImplementedError(
                f"{k=} is not valid. Chose in {str(set(KmerTypeMap))}"
            )
        return map(lambda e: Kmer(e, k), KmerTypeMap[k].enumerate_kmer(self.data))
