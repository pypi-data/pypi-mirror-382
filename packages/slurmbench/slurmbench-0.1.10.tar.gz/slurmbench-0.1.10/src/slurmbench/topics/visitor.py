"""Interface for topics visitor."""

from __future__ import annotations

import logging
from abc import abstractmethod
from enum import StrEnum
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    import slurmbench.topic.description as topic_desc
    import slurmbench.topic.visitor as topic_visitor

_LOGGER = logging.getLogger(__name__)


class Topics(StrEnum):
    """Topics."""

    @classmethod
    def from_description(
        cls,
        topic_description: topic_desc.Description,
    ) -> Self:
        """Create topic from description.

        Raises
        ------
        ValueError
            The topic does not have a tool named `tool_name`.
        """
        try:
            return cls(topic_description.name())
        except ValueError as exc:
            _LOGGER.exception(
                "Unknown topic `%s`",
                topic_description.name(),
            )
            raise ValueError from exc

    @abstractmethod
    def to_description(self) -> topic_desc.Description:
        """Get topic description."""
        raise NotImplementedError

    @abstractmethod
    def tools(self) -> type[topic_visitor.Tools]:
        """Get tools."""
        raise NotImplementedError
