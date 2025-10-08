"""Sample missing inputs."""

from __future__ import annotations

import logging
from enum import StrEnum
from typing import TYPE_CHECKING

import slurmbench.experiment.managers as exp_managers
import slurmbench.tool.connector as tool_connector
import slurmbench.tool.results as tool_res
from slurmbench import tab_files

from . import file_system as smp_fs
from . import items as smp
from . import status as smp_status

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

_LOGGER = logging.getLogger(__name__)


class MissingInput:
    """Missing input item."""

    @classmethod
    def from_tool_input(
        cls,
        arg_name: str,
        tool_input: tool_res.Result,
        reason: smp_status.Error,
        help_string: str,
    ) -> MissingInput:
        """Create missing input from tool input."""
        return cls(
            str(arg_name),
            tool_input.exp_fs_manager().topic_dir().name,
            tool_input.exp_fs_manager().tool_dir().name,
            tool_input.exp_fs_manager().exp_dir().name,
            reason,
            help_string,
        )

    def __init__(  # noqa: PLR0913
        self,
        arg_name: str,
        topic_name: str,
        tool_name: str,
        experiment_name: str,
        reason: smp_status.Error,
        help_string: str,
    ) -> None:
        """Initialize."""
        self.__arg_name = arg_name
        self.__topic_name = topic_name
        self.__tool_name = tool_name
        self.__exp_name = experiment_name
        self.__reason = reason
        self.__help_string = help_string

    def arg_name(self) -> str:
        """Get argument name."""
        return self.__arg_name

    def topic_name(self) -> str:
        """Get topic name."""
        return self.__topic_name

    def tool_name(self) -> str:
        """Get tool name."""
        return self.__tool_name

    def experiment_name(self) -> str:
        """Get experiment name."""
        return self.__exp_name

    def reason(self) -> smp_status.Error:
        """Get reason."""
        return self.__reason

    def help(self) -> str:
        """Get help string."""
        return self.__help_string


class MissingInputsTSVHeader(StrEnum):
    """Missing inputs TSV header."""

    ARG_NAME = "arg_name"
    TOPIC = "input_topic"
    TOOL = "input_tool"
    EXPERIMENT = "input_experiment"
    REASON = "reason"
    HELP = "help"


class MissingInputsTSVReader(tab_files.TSVReader[MissingInputsTSVHeader, MissingInput]):
    """Missing inputs TSV reader."""

    def __iter__(self) -> Iterator[MissingInput]:
        """Iterate over missing inputs items."""
        for row in self._csv_reader:
            yield MissingInput(
                self._get_cell(row, MissingInputsTSVHeader.ARG_NAME),
                self._get_cell(row, MissingInputsTSVHeader.TOPIC),
                self._get_cell(row, MissingInputsTSVHeader.TOOL),
                self._get_cell(row, MissingInputsTSVHeader.TOOL),
                smp_status.Error(
                    self._get_cell(row, MissingInputsTSVHeader.REASON),
                ),
                self._get_cell(row, MissingInputsTSVHeader.HELP),
            )


class MissingInputsTSVWriter(tab_files.TSVWriter[MissingInputsTSVHeader, MissingInput]):
    """Missing inputs TSV writer."""

    def _to_cell(self, item: MissingInput, column_id: MissingInputsTSVHeader) -> object:
        """Get cell from item."""
        match column_id:
            case MissingInputsTSVHeader.ARG_NAME:
                return item.arg_name()
            case MissingInputsTSVHeader.TOPIC:
                return item.topic_name()
            case MissingInputsTSVHeader.TOOL:
                return item.tool_name()
            case MissingInputsTSVHeader.EXPERIMENT:
                return item.experiment_name()
            case MissingInputsTSVHeader.REASON:
                return item.reason()
            case MissingInputsTSVHeader.HELP:
                return item.help()


def write_sample_missing_inputs(
    exp_manager: exp_managers.WithArguments,
    row_numbered_sample: smp.RowNumbered,
    sample_missing_inputs: Iterable[MissingInput],
) -> None:
    """Write sample missing inputs."""
    data_sample_fs_manager = exp_manager.data_fs_manager().sample_fs_manager(
        row_numbered_sample,
    )
    smp_fs.reset_sample_dir(data_sample_fs_manager)
    with MissingInputsTSVWriter.open(
        data_sample_fs_manager.missing_inputs_tsv(),
        "w",
    ) as out_miss_inputs:
        out_miss_inputs.write_bunch(sample_missing_inputs)


def for_sample[N: tool_connector.Names](
    tool_inputs: dict[N, tool_res.Result],
    sample: smp.RowNumbered,
) -> list[MissingInput]:
    """Get a list of missing inputs."""
    list_missing_inputs: list[MissingInput] = []
    for arg_name, tool_input in tool_inputs.items():
        input_status = tool_input.check(sample)
        match input_status:
            case smp_status.Error():
                list_missing_inputs.append(
                    MissingInput.from_tool_input(
                        str(arg_name),
                        tool_input,
                        input_status,
                        _get_help_str(tool_input),
                    ),
                )
    return list_missing_inputs


def _get_help_str(tool_input: tool_res.Result) -> str:
    """Get help string."""
    return (
        "pbfbench"
        f" {tool_input.exp_fs_manager().tool_description().topic().cmd()}"
        f" {tool_input.exp_fs_manager().tool_description().cmd()}"
        f" run"
        " --help"
    )
