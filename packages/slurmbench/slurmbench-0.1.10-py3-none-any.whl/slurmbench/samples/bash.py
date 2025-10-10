"""Sample bash script logics."""

from collections.abc import Iterator
from enum import StrEnum
from pathlib import Path

import slurmbench.bash.items as bash_items
import slurmbench.experiment.file_system as exp_fs
import slurmbench.samples.file_system as smp_fs
import slurmbench.slurm.bash as slurm_bash


class SampleUIDLinesBuilder:
    """Sample UID bash lines builder."""

    SAMPLES_TSV_VAR = bash_items.Variable("SAMPLES_TSV")

    SAMPLE_UID_VAR = bash_items.Variable("SAMPLE_UID")

    def __init__(self, samples_file: Path) -> None:
        """Initialize."""
        self.__samples_file = samples_file

    def samples_file(self) -> Path:
        """Get samples file."""
        return self.__samples_file

    def lines(self) -> Iterator[str]:
        """Give the bash lines defining the species-sample id variable."""
        yield self.SAMPLES_TSV_VAR.set(bash_items.path_to_str(self.__samples_file))
        yield self.SAMPLE_UID_VAR.set(
            get_sample_attribute(self.__samples_file, smp_fs.TSVHeader.UID),
        )
        yield f"echo {self.SAMPLE_UID_VAR.eval()}"


def get_sample_attribute(samples_file: Path, attribute: str | StrEnum) -> str:
    """Get sample attribute."""
    # DOCU user can use it to define bash tool commands
    attribute_column_index = smp_fs.columns_name_index(samples_file)[str(attribute)]
    return (
        f"$("
        f'sed -n "{slurm_bash.SLURM_ARRAY_TASK_ID_VAR.eval()}p"'
        f" {SampleUIDLinesBuilder.SAMPLES_TSV_VAR.eval()}"
        f" | cut -f{1 + attribute_column_index}"
        f")"
    )


def sample_shell_fs_manager(exp_fs_manager: exp_fs.ManagerBase) -> smp_fs.Manager:
    """Get sample shell variable file system manager."""
    return smp_fs.Manager(
        exp_fs_manager.sample_dir(SampleUIDLinesBuilder.SAMPLE_UID_VAR.eval()),
    )
