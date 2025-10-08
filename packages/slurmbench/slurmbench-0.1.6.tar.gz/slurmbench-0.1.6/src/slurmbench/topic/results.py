"""Abstract tools results items module."""

from abc import ABC, abstractmethod
from collections.abc import Callable

import slurmbench.experiment.file_system as exp_fs
import slurmbench.samples.items as smp
import slurmbench.tool.results as tool_res

from . import visitor


class Error:
    """Error to get the result."""

    def __init__(self, msg: str) -> None:
        """Initialize."""
        self.__msg = msg

    def __str__(self) -> str:
        """Get the error message."""
        return self.__msg


# Separate the visitor from the result class
# because some result are really specific, other are conventionnal.
# Only conventionnal results have a visitor.
class Visitor[T: visitor.Tools, R: tool_res.Result](ABC):
    """Abstract result visitor."""

    @classmethod
    @abstractmethod
    def result_builder(cls) -> type[R]:
        """Get result builder."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def result_builder_from_tool(cls, tool: T) -> Error | type[R]:
        """Get result builder."""
        raise NotImplementedError

    @classmethod
    def tool_gives_the_result(cls, tool: T) -> bool:
        """Check if the tool gives the result."""
        return not isinstance(cls.result_builder_from_tool(tool), Error)


class OriginalVisitor[T: visitor.Tools, OriginalResult: tool_res.Original](
    Visitor[T, OriginalResult],
):
    """Original result visitor."""


type ConvertFn[FormattedResult: tool_res.Formatted] = Callable[
    [exp_fs.DataManager, smp.RowNumbered],
    FormattedResult,
]


class FormattedVisitor[T: visitor.Tools, FormattedResult: tool_res.Formatted](
    Visitor[T, FormattedResult],
):
    """Formatted result visitor."""

    @classmethod
    @abstractmethod
    def convert_fn(
        cls,
        tool: T,
    ) -> Error | ConvertFn[FormattedResult]:
        """Get convert function."""
        raise NotImplementedError

    @classmethod
    def result_builder_from_tool(
        cls,
        tool: T,
    ) -> Error | type[FormattedResult]:
        """Get result builder."""
        match convert_fn_or_err := cls.convert_fn(tool):
            case Error():
                return convert_fn_or_err
            case _:
                return cls.result_builder()
