"""Topic abstract application module."""

# Due to typer usage:
# ruff: noqa: TC001, TC003

from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import Self

import typer

import slurmbench.topic.visitor as topic_visitor

from . import description as desc

_LOGGER = logging.getLogger(__name__)


class Topic[ToolsT: type[topic_visitor.Tools]]:
    """Topic application."""

    @classmethod
    def new(
        cls,
        topic_description: desc.Description,
        tools: ToolsT,
        tool_apps: Iterable[typer.Typer],
    ) -> Self:
        """Build topic application."""
        tool_apps = list(tool_apps)
        if len(tool_apps) != len(tools):
            _LOGGER.critical(
                "Number of tool applications (%d)"
                " differs from number of tools (%d) for topic `%s`",
                len(tool_apps),
                len(tools),
                topic_description.name(),
            )
            raise typer.Exit(1)
        app = typer.Typer(
            name=topic_description.cmd(),
            help=f"Subcommand for topic `{topic_description.name()}`",
            rich_markup_mode="rich",
        )
        for tool_app in tool_apps:
            app.add_typer(tool_app)
        return cls(tools, app)

    def __init__(self, tools: ToolsT, app: typer.Typer) -> None:
        self._tools = tools
        self._app = app

    def tools(self) -> ToolsT:
        """Get tools."""
        return self._tools

    def app(self) -> typer.Typer:
        """Get app."""
        return self._app
