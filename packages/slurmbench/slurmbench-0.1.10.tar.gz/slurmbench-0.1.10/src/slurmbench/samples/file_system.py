"""Sample file system manager."""

from __future__ import annotations

import shutil
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, final

from slurmbench import tab_files

from . import items as smp
from .slurm import file_system as slurm_fs

if TYPE_CHECKING:
    from collections.abc import Iterator


class Manager:
    """Sample file system manager."""

    MISSING_INPUTS_TSV_NAME = Path("missing_inputs.tsv")
    ERRORS_LOG_NAME = Path("errors.log")
    DONE_LOG_NAME = Path("done.log")

    @classmethod
    def from_exp_dir_and_sample(
        cls,
        exp_dir: Path,
        sample: smp.RowNumbered,
    ) -> Manager:
        """Get sample experiment file system manager."""
        return cls(exp_dir / sample.uid())

    def __init__(self, sample_dir: Path) -> None:
        """Inititialize."""
        self.__sample_dir = sample_dir
        self.__slurm_fs_manager = slurm_fs.Manager(self.__sample_dir)

    def sample_dir(self) -> Path:
        """Get sample directory path."""
        return self.__sample_dir

    def missing_inputs_tsv(self) -> Path:
        """Get missing_inputs file path."""
        return self.__sample_dir / self.MISSING_INPUTS_TSV_NAME

    def errors_log(self) -> Path:
        """Get errors file."""
        return self.__sample_dir / self.ERRORS_LOG_NAME

    def done_log(self) -> Path:
        """Get done file."""
        return self.__sample_dir / self.DONE_LOG_NAME

    def slurm_fs_manager(self) -> slurm_fs.Manager:
        """Get slurm file system manager."""
        return self.__slurm_fs_manager


def reset_sample_dir(manager: Manager) -> None:
    """Reset sample directory."""
    shutil.rmtree(manager.sample_dir(), ignore_errors=True)
    manager.sample_dir().mkdir(parents=True, exist_ok=True)


class TSVHeader(StrEnum):
    """TSV header."""

    UID = "uid"


@final
class TSVReader(tab_files.TSVReader[TSVHeader, smp.RowNumbered]):
    """Samples TSV reader."""

    @classmethod
    def header_type(cls) -> type[TSVHeader]:
        """Get header type."""
        return TSVHeader

    def __iter__(self) -> Iterator[smp.RowNumbered]:
        """Iterate sequence probability scores."""
        for row_idx, row in enumerate(self._csv_reader, start=1):
            yield smp.RowNumbered(row_idx, self._get_cell(row, TSVHeader.UID))


def columns_name_index(file: Path) -> dict[str, int]:
    """Get columns name index."""
    with TSVReader.open(file) as reader:
        return reader.header_map().indices()
