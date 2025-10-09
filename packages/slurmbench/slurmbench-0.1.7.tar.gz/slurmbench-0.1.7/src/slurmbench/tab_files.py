"""Tabular files."""

import _csv
import csv
from abc import ABC, abstractmethod
from collections.abc import Generator, Iterable, Iterator
from contextlib import contextmanager
from enum import StrEnum
from pathlib import Path
from typing import Literal, Self, final

type WriteMode = Literal["w", "a"]


class HeaderMap:
    """Header map."""

    def __init__(self, col_id: list[str]) -> None:
        self.__col_id = col_id
        self.__col_idx = {name: idx for idx, name in enumerate(col_id)}

    def names(self) -> list[str]:
        """Get column names."""
        return self.__col_id

    def indices(self) -> dict[str, int]:
        """Get column indices."""
        return self.__col_idx

    def id_from_idx(self, idx: int) -> str:
        """Get column ID from index."""
        return self.__col_id[idx]

    def idx_from_id(self, name: str) -> int:
        """Get column index from ID."""
        return self.__col_idx[name]


class Delimiter(ABC):
    """Tabular file delimiter."""

    @classmethod
    @abstractmethod
    def char(cls) -> str:
        """Get delimiter character."""
        raise NotImplementedError


class _Base[H: StrEnum, D: Delimiter](ABC):
    """Reader and writer base class."""

    @classmethod
    @abstractmethod
    def header_type(cls) -> type[H]:
        """Get header."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def delimiter(cls) -> type[D]:
        """Get delimiter type."""
        raise NotImplementedError

    def __init__(self, file: Path, header_map: HeaderMap) -> None:
        self._file = file
        self._header_map = header_map

    def file(self) -> Path:
        """Get file."""
        return self._file

    def header_map(self) -> HeaderMap:
        """Get header map."""
        return self._header_map


class Reader[H: StrEnum, D: Delimiter, T](_Base[H, D]):
    """Tabular file reader."""

    @classmethod
    @contextmanager
    def open(cls, file: Path) -> Generator[Self]:
        """Open TSV file for reading."""
        with file.open() as f_in:
            reader = cls(file, csv.reader(f_in, delimiter=cls.delimiter().char()))
            yield reader

    def __init__(self, file: Path, csv_reader: _csv.Reader) -> None:
        """Initialize object."""
        self._csv_reader = csv_reader
        super().__init__(file, HeaderMap(next(self._csv_reader)))

    @abstractmethod
    def __iter__(self) -> Iterator[T]:
        """Iterate over the items."""
        raise NotImplementedError

    def _get_cell(self, row: list[str], column_id: H) -> str:
        return row[self._header_map.idx_from_id(column_id)]


class Writer[H: StrEnum, D: Delimiter, T](_Base[H, D]):
    """Unresolved samples TSV writer."""

    @classmethod
    @abstractmethod
    def reader_type(cls) -> type[Reader[H, D, T]]:
        """Get reader."""
        raise NotImplementedError

    @classmethod
    @contextmanager
    def auto_open(cls, file: Path) -> Generator[Self]:
        """Open TSV file for writing."""
        mode: WriteMode = "a" if file.exists() else "w"
        with cls.open(file, mode) as writer:
            yield writer

    @classmethod
    @contextmanager
    def open(cls, file: Path, mode: WriteMode) -> Generator[Self]:
        """Open TSV file for writing."""
        match mode:
            case "w":
                header_map = None
            case "a":
                if file.exists():
                    with cls.reader_type().open(file) as reader:
                        header_map = reader.header_map()
                else:
                    header_map = None
        with file.open(mode) as f_out:
            writer = cls(
                file,
                csv.writer(f_out, delimiter=cls.delimiter().char()),
                header_map,
            )
            yield writer

    def __init__(
        self,
        file: Path,
        csv_writer: _csv.Writer,
        header_map: HeaderMap | None,
    ) -> None:
        """Initialize object."""
        self._csv_writer = csv_writer
        super().__init__(
            file,
            (header_map if header_map is not None else self._write_header()),
        )

    def write(self, item: T) -> None:
        """Write row."""
        self._csv_writer.writerow(
            [
                self._to_cell(item, self.header_type()(name))
                for name in self._header_map.names()
            ],
        )

    def write_bunch(self, items: Iterable[T]) -> None:
        """Write bunch of rows."""
        for item in items:
            self.write(item)

    @abstractmethod
    def _to_cell(self, item: T, column_id: H) -> object:
        """Get cell from item."""
        raise NotImplementedError

    def _write_header(self) -> HeaderMap:
        header_row = list(map(str, self.header_type()))
        self._csv_writer.writerow(header_row)
        return HeaderMap(header_row)


@final
class TSVDelimiter(Delimiter):
    """Tabular file delimiter."""

    @classmethod
    def char(cls) -> str:
        """Get delimiter character."""
        return "\t"


class TSVReader[H: StrEnum, T](Reader[H, TSVDelimiter, T]):
    """TSV file reader."""

    @classmethod
    def delimiter(cls) -> type[TSVDelimiter]:
        """Get delimiter."""
        return TSVDelimiter


class TSVWriter[H: StrEnum, T](Writer[H, TSVDelimiter, T]):
    """TSV file writer."""

    @classmethod
    def delimiter(cls) -> type[TSVDelimiter]:
        """Get delimiter."""
        return TSVDelimiter
