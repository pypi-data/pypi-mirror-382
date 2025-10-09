"""Topic visitor abstract module."""

from __future__ import annotations

import logging
from abc import abstractmethod
from enum import StrEnum
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    import slurmbench.tool.description as tool_desc


_LOGGER = logging.getLogger(__name__)


class Tools(StrEnum):
    """Topic tools."""

    @classmethod
    def from_description(
        cls,
        tool_description: tool_desc.Description,
    ) -> Self:
        """Create tool from description.

        Raises
        ------
        ValueError
            The topic does not have a tool named `tool_name`.
        """
        try:
            return cls(tool_description.name())
        except ValueError as exc:
            _LOGGER.exception(
                "Unknown tool `%s` for topic `%s`",
                tool_description.name(),
                tool_description.name(),
            )
            raise ValueError from exc

    @abstractmethod
    def to_description(self) -> tool_desc.Description:
        """Get tool description."""
        raise NotImplementedError
