"""Experiment errors module."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, final

import slurmbench.samples.items as smp
import slurmbench.samples.status as smp_status
from slurmbench import tab_files

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from . import file_system as exp_fs


class SampleError:
    """Sample error."""

    @classmethod
    def sample_with_missing_inputs(
        cls,
        sample_item: smp.RowNumbered,
    ) -> SampleError:
        """Instantiate a sample error with a missing inputs reason."""
        return cls(sample_item.uid(), smp_status.Error.MISSING_INPUTS)

    @classmethod
    def sample_with_error(
        cls,
        sample_item: smp.RowNumbered,
    ) -> SampleError:
        """Instantiate a sample error with an error reason."""
        return cls(sample_item.uid(), smp_status.Error.ERROR)

    def __init__(self, uid: str, reason: smp_status.Error) -> None:
        """Initialize."""
        self.__uid = uid
        self.__reason = reason

    def uid(self) -> str:
        """Get sample UID."""
        return self.__uid

    def reason(self) -> smp_status.Error:
        """Get reason."""
        return self.__reason


class ErrorsTSVHeader(StrEnum):
    """Error samples TSV header."""

    UID = "uid"
    REASON = "reason"


@final
class ErrorsTSVReader(tab_files.TSVReader[ErrorsTSVHeader, SampleError]):
    """Error samples TSV reader."""

    @classmethod
    def header_type(cls) -> type[ErrorsTSVHeader]:
        """Get header type."""
        return ErrorsTSVHeader

    def __iter__(self) -> Iterator[SampleError]:
        """Iterate over error samples."""
        for row in self._csv_reader:
            sample_uid = self._get_cell(row, self.header_type().UID)
            error_status = smp_status.Error(
                self._get_cell(row, self.header_type().REASON),
            )
            yield SampleError(sample_uid, error_status)


@final
class ErrorsTSVWriter(tab_files.TSVWriter[ErrorsTSVHeader, SampleError]):
    """Error samples TSV writer."""

    @classmethod
    def header_type(cls) -> type[ErrorsTSVHeader]:
        """Get header type."""
        return ErrorsTSVHeader

    @classmethod
    def reader_type(cls) -> type[ErrorsTSVReader]:
        """Get reader type."""
        return ErrorsTSVReader

    def _to_cell(self, item: SampleError, column_id: ErrorsTSVHeader) -> object:
        """Get cell from item."""
        match column_id:
            case ErrorsTSVHeader.UID:
                return item.uid()
            case ErrorsTSVHeader.REASON:
                return item.reason()

    def write_error_sample(self, error_sample: SampleError) -> None:
        """Write error sample."""
        self.write(error_sample)

    def write_error_samples(self, error_samples: Iterable[SampleError]) -> None:
        """Write error samples."""
        for error_sample in error_samples:
            self.write_error_sample(error_sample)


def write_missing_inputs(
    data_fs_manager: exp_fs.DataManager,
    samples_with_missing_inputs: Iterable[smp.RowNumbered],
) -> None:
    """Write experiment missing inputs."""
    with ErrorsTSVWriter.auto_open(data_fs_manager.errors_tsv()) as out_exp_errors:
        out_exp_errors.write_error_samples(
            (
                SampleError.sample_with_missing_inputs(row_numbered_item)
                for row_numbered_item in samples_with_missing_inputs
            ),
        )


def write_errors(
    data_fs_manager: exp_fs.DataManager,
    samples_with_errors: Iterable[smp.RowNumbered],
) -> None:
    """Write experiment errors."""
    with ErrorsTSVWriter.auto_open(data_fs_manager.errors_tsv()) as out_exp_errors:
        out_exp_errors.write_error_samples(
            (
                SampleError.sample_with_error(row_numbered_item)
                for row_numbered_item in samples_with_errors
            ),
        )
