import vizibridge._vizibridge as rust_types
from vizibridge.kmers import Kmer, KmerType
from vizibridge.DNA import DNA
from vizibridge.kmer_set import KmerSet
from typing import Iterator, Tuple
from typing_extensions import Self
from collections.abc import Mapping
from pathlib import Path

from typing import Set, Mapping as MapAnnot


kmer_indexes = [
    getattr(rust_types, a) for a in dir(rust_types) if a.startswith("KmerIndex")
]

KmerIndexType = kmer_indexes[0]
for t in kmer_indexes[1:]:
    KmerIndexType |= t

KmerIndexTypeMap = dict()
for KT in kmer_indexes:
    if KT.val_type() == 64:
        KmerIndexTypeMap[KT.size()] = KT


class KmerIndex(Mapping):
    __slots__ = ("__base_index", "__k")

    def __init__(self, path: Path, k: int):
        if not path.exists():
            raise IOError(path)
        self.__base_index = KmerIndexTypeMap[k](str(path))
        self.__k = k

    @property
    def k(self):
        return self.__k

    @property
    def base_index(self):
        return self.__base_index

    def __getitem__(self, kmer: KmerType | Kmer):
        if not isinstance(kmer, KmerType):
            kmer = kmer.base_type
        return self.__base_index[kmer]

    def get_all(self, kmer: KmerType | Kmer):
        return self.__base_index.get_all(kmer)

    def __len__(self):
        return len(self.__base_index)

    def items_iter(self):
        return iter(self.__base_index)

    def __iter__(self):
        yield from (index_entry[0] for index_entry in self.items_iter())

    @classmethod
    def build(
        cls,
        iterator: Iterator[Tuple[Kmer, int]],
        index_path: Path | str,
        k: int,
        buffer_size=10**7,
    ) -> Self:
        if isinstance(index_path, str):
            index_path = Path(index_path)
        BaseIndexType = KmerIndexTypeMap[k]
        if index_path.exists():
            raise IOError("path already exists")
        iterator = map(
            lambda e: (getattr(e[0], "base_type", e[0]), e[1]),
            iterator,
        )
        BaseIndexType.build(iterator, str(index_path), buffer_size=buffer_size)
        return cls(index_path, k)

    @classmethod
    def build_dna(
        cls,
        iterator: Iterator[Tuple[DNA, int]],
        index_path: Path | str,
        k: int,
        index: int,
        modulo: int,
        buffer_size=10**7,
    ) -> Self:
        if isinstance(index_path, str):
            index_path = Path(index_path)
        BaseIndexType = KmerIndexTypeMap[k]
        if index_path.exists():
            raise IOError("path already exists")
        iterator = map(
            lambda e: (getattr(e[0], "data", e[0]), e[1]),
            iterator,
        )
        BaseIndexType.build_dna(
            iterator,
            str(index_path),
            buffer_size=buffer_size,
            index=index,
            modulo=modulo,
        )
        return cls(index_path, k)

    def join(
        self,
        iterator: Iterator[Tuple[Kmer, int]],
        out_path: Path | str,
        buffer_size=10**7,
    ) -> MapAnnot[int, int]:
        if isinstance(out_path, str):
            out_path = Path(out_path)
        if out_path.exists():
            raise IOError("path already exists")
        return self.base_index.join_iteru64(iterator, str(out_path), buffer_size)

    def intersection(
        self, iterator: Iterator[Kmer], out_path: Path | str, buffer_size=10**7
    ) -> Set[int]:
        if isinstance(out_path, str):
            out_path = Path(out_path)
        if out_path.exists():
            raise IOError("path already exists")
        return self.base_index.intersection_iter(iterator, str(out_path), buffer_size)

    def get_from_dnas(self, iterator: Iterator[DNA]) -> list[tuple[KmerType, int]]:
        dnas_it = (getattr(dna, "data", dna) for dna in iterator)
        return self.base_index.get_from_dnas(dnas_it)

    def get_from_dna(self, *dnas: DNA) -> list[tuple[KmerType, int]]:
        return self.get_from_dnas(dnas)

    def intersection_index(
        self, other: KmerSet, out_path: Path | str, buffer_size=10**7
    ) -> MapAnnot[int, int]:
        if isinstance(out_path, str):
            out_path = Path(out_path)
        if out_path.exists():
            raise IOError("path already exists")
        return self.base_index.intersection_index(
            other.base_index, str(out_path), buffer_size
        )

    def join_index(
        self, other: Self, out_path: Path | str, buffer_size=10**7
    ) -> MapAnnot[int, int]:
        if isinstance(out_path, str):
            out_path = Path(out_path)
        if out_path.exists():
            raise IOError("path already exists")
        return self.base_index.join_indexu64(
            other.base_index, str(out_path), buffer_size
        )

    def extract_uniq(self, out_path: Path, buffer_size=10**7) -> Self:
        if isinstance(out_path, str):
            out_path = Path(out_path)
        if out_path.exists():
            raise IOError("path already exists")
        return self.base_index.extract_uniq(str(out_path), buffer_size)
