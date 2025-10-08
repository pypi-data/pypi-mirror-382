"""Tool shell prelude."""

# Due to typer usage:
# ruff: noqa: PLC0414, F401

from slurmbench.bash.items import Variable as BashVar
from slurmbench.samples.bash import get_sample_attribute as get_sample_attribute
from slurmbench.tool.bash import Argument as Argument
from slurmbench.tool.bash import OnlyOptions as OnlyOptions
