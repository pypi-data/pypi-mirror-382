"""Experience monitors."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, final

import slurmbench.samples.items as smp
import slurmbench.samples.status as smp_status
from slurmbench import tab_files

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from . import file_system as exp_fs


class UnresolvedSamplesTSVHeader(StrEnum):
    """Unresolved samples TSV header."""

    ROW_NUMBER = "row_number"
    SAMPLE_UID = "sample_uid"


@final
class UnresolvedSamplesTSVReader(
    tab_files.TSVReader[UnresolvedSamplesTSVHeader, smp.RowNumbered],
):
    """Unresolved samples TSV reader."""

    @classmethod
    def header_type(cls) -> type[UnresolvedSamplesTSVHeader]:
        """Get header."""
        return UnresolvedSamplesTSVHeader

    def __iter__(self) -> Iterator[smp.RowNumbered]:
        """Iterate over unresolved samples."""
        for row in self._csv_reader:
            row_number = int(self._get_cell(row, self.header_type().ROW_NUMBER))
            sample_uid = self._get_cell(row, self.header_type().SAMPLE_UID)
            yield smp.RowNumbered(row_number, sample_uid)


@final
class UnresolvedSamplesTSVWriter(
    tab_files.TSVWriter[UnresolvedSamplesTSVHeader, smp.RowNumbered],
):
    """Unresolved samples TSV writer."""

    @classmethod
    def header_type(cls) -> type[UnresolvedSamplesTSVHeader]:
        """Get header."""
        return UnresolvedSamplesTSVHeader

    @classmethod
    def reader_type(cls) -> type[UnresolvedSamplesTSVReader]:
        """Get reader."""
        return UnresolvedSamplesTSVReader

    def _to_cell(
        self,
        item: smp.RowNumbered,
        column_id: UnresolvedSamplesTSVHeader,
    ) -> object:
        """Get cell from item."""
        match column_id:
            case UnresolvedSamplesTSVHeader.ROW_NUMBER:
                return item.row_number()
            case UnresolvedSamplesTSVHeader.SAMPLE_UID:
                return item.uid()


class ResolvedSample:
    """Resolved sample."""

    def __init__(
        self,
        sample_uid: str,
        status: smp_status.Status,
    ) -> None:
        """Initialize."""
        self.__sample_uid = sample_uid
        self.__status = status

    def sample_uid(self) -> str:
        """Get sample UID."""
        return self.__sample_uid

    def status(self) -> smp_status.Status:
        """Get satus."""
        return self.__status


class ResolvedSamplesTSVHeader(StrEnum):
    """Resolved samples TSV header."""

    SAMPLE_UID = "sample_uid"
    STATUS = "status"


@final
class ResolvedSampleTSVReader(
    tab_files.TSVReader[ResolvedSamplesTSVHeader, ResolvedSample],
):
    """Error samples TSV reader."""

    @classmethod
    def header_type(cls) -> type[ResolvedSamplesTSVHeader]:
        """Get header type."""
        return ResolvedSamplesTSVHeader

    def __iter__(self) -> Iterator[ResolvedSample]:
        """Iterate over resolved samples."""
        for row in self._csv_reader:
            sample_uid = self._get_cell(row, self.header_type().SAMPLE_UID)
            status = smp_status.from_str(
                self._get_cell(row, self.header_type().STATUS),
            )
            yield ResolvedSample(sample_uid, status)


@final
class ResolvedSamplesTSVWriter(
    tab_files.TSVWriter[ResolvedSamplesTSVHeader, ResolvedSample],
):
    """Resolved samples TSV writer."""

    @classmethod
    def header_type(cls) -> type[ResolvedSamplesTSVHeader]:
        """Get header type."""
        return ResolvedSamplesTSVHeader

    @classmethod
    def reader_type(cls) -> type[ResolvedSampleTSVReader]:
        """Get reader."""
        return ResolvedSampleTSVReader

    def _to_cell(
        self,
        item: ResolvedSample,
        column_id: ResolvedSamplesTSVHeader,
    ) -> object:
        """Get cell from item."""
        match column_id:
            case ResolvedSamplesTSVHeader.SAMPLE_UID:
                return item.sample_uid()
            case ResolvedSamplesTSVHeader.STATUS:
                return item.status()


def write_unresolved_samples(
    work_fs_manager: exp_fs.WorkManager,
    samples: Iterable[smp.RowNumbered],
) -> None:
    """Write unresolved samples."""
    with UnresolvedSamplesTSVWriter.auto_open(
        work_fs_manager.unresolved_samples_tsv(),
    ) as writer:
        writer.write_bunch(samples)


def write_resolved_samples(
    work_fs_manager: exp_fs.WorkManager,
    samples_with_status: Iterable[tuple[smp.RowNumbered, smp_status.Status]],
) -> None:
    """Write resolved samples."""
    with ResolvedSamplesTSVWriter.auto_open(
        work_fs_manager.resolved_samples_tsv(),
    ) as writer:
        writer.write_bunch(
            ResolvedSample(sample.uid(), status)
            for sample, status in samples_with_status
        )


def update_samples_resolution_status(
    work_fs_manager: exp_fs.WorkManager,
    samples_with_status: Iterable[tuple[smp.RowNumbered, smp_status.Status]],
) -> None:
    """Move resolved samples from unresolved file to resolved file."""
    samples_with_status = list(samples_with_status)
    write_resolved_samples(work_fs_manager, samples_with_status)

    with UnresolvedSamplesTSVReader.open(
        work_fs_manager.unresolved_samples_tsv(),
    ) as reader:
        resolved_sample_row_numbers = {
            sample.row_number() for sample, _ in samples_with_status
        }
        new_unresolved_samples = [
            sample
            for sample in reader
            if sample.row_number() not in resolved_sample_row_numbers
        ]

    with UnresolvedSamplesTSVWriter.open(
        work_fs_manager.unresolved_samples_tsv(),
        "w",
    ) as writer:
        writer.write_bunch(new_unresolved_samples)


def iter_unresolved_samples(
    work_fs_manager: exp_fs.WorkManager,
) -> Iterator[smp.RowNumbered]:
    """Iterate over unresolved samples."""
    with UnresolvedSamplesTSVReader.open(
        work_fs_manager.unresolved_samples_tsv(),
    ) as reader:
        yield from reader


def iter_resolved_samples(
    work_fs_manager: exp_fs.WorkManager,
) -> Iterator[ResolvedSample]:
    """Iterate over resolved samples."""
    with ResolvedSampleTSVReader.open(
        work_fs_manager.resolved_samples_tsv(),
    ) as reader:
        yield from reader
