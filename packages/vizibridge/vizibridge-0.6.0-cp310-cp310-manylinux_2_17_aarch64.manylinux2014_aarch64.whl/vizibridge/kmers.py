import vizibridge._vizibridge as rust_types
from vizibridge._vizibridge import PyNucleotid as RustNucleotid
from typing_extensions import Self

Pykmers = [getattr(rust_types, a) for a in dir(rust_types) if a.startswith("PyKmer")]

BytesSerial = [
    getattr(rust_types, a) for a in dir(rust_types) if a.startswith("BytesSerial")
]

KmerType = Pykmers[0]
for t in Pykmers[1:]:
    KmerType |= t

KmerTypeMap = {KT.size(): KT for KT in Pykmers}
ByteSerialMap = {BS.size(): BS for BS in BytesSerial}


class Kmer:
    __slots__ = ("__data",)

    def __init__(self, data: KmerType | int | bytes, size: int | None = None):
        if isinstance(data, int):
            assert size
            data = KmerTypeMap[size](data)
        elif isinstance(data, bytes):
            assert size
            serialData = ByteSerialMap[size](data)
            data = KmerTypeMap[size](serialData)
        self.__data = data

    def __getstate__(self):
        return dict(base_cls=type(self.__data).size(), data=self.__data.data)

    def __setstate__(self, state):
        self.__data = KmerTypeMap[state["base_cls"]](state["data"])

    @classmethod
    def from_sequence(cls, seq) -> Self:
        k = len(seq)
        if k not in KmerTypeMap:
            raise ValueError(
                "Input sequence of invalid size to build a kmer (got {len(seq)})"
            )
        if isinstance(seq, str):
            return Kmer(KmerTypeMap[k].from_str(seq), k)
        seq = getattr(seq, "data")
        if isinstance(seq, rust_types.PyDNA):
            return Kmer(KmerTypeMap[k].from_dna(seq), k)
        raise NotImplementedError(
            f"conversion of Kmer from {type(seq)} not possible. Use DNA or str types"
        )

    @property
    def size(self) -> int:
        return type(self.__data).size()

    @property
    def data(self) -> int | bytes:
        data = self.__data.data
        if isinstance(data, int):
            return data
        return bytes(data)

    @property
    def base_type(self) -> KmerType:
        return self.__data

    def __repr__(self):
        return repr(self.__data)

    def __str__(self):
        return str(self.__data)

    def __hash__(self):
        return hash(self.__data)

    def add_left_nucleotid(self, c: str | rust_types.PyNucleotid) -> Self:
        if isinstance(c, str):
            c = RustNucleotid.from_char(c)
        return type(self)(self.__data.add_left_nucleotid(c))

    def add_right_nucleotid(self, c: str) -> Self:
        if isinstance(c, str):
            c = RustNucleotid.from_char(c)
        return type(self)(self.__data.add_right_nucleotid(c))

    def reverse_complement(self) -> Self:
        return type(self)(self.__data.reverse_complement())

    def is_canonical(self) -> bool:
        return self.__data.is_canonical()

    def canonical(self) -> Self:
        return type(self)(self.__data.canonical())

    def __lt__(self, other) -> bool:
        return self.__data < other.__data

    def __gt__(self, other) -> bool:
        return self.__data < other.__data

    def __eq__(self, other) -> bool:
        return (
            type(self) is type(other)
            and self.size == other.size
            and self.data == other.data
        )
