"""ABC for apps."""

# Due to typer usage:

from __future__ import annotations

import logging
from enum import StrEnum
from typing import TYPE_CHECKING

import typer

from .help import app as help_app
from .slurm import app as slurm_app

if TYPE_CHECKING:
    from collections.abc import Iterable

    from .topic import app as topic_app
    from .topics import visitor as topics_visitor

_LOGGER = logging.getLogger(__name__)


class CommandCategories(StrEnum):
    """Command categories."""

    TOPICS = "Topics"
    UTILITIES = "Utilities"


def new(
    name: str,
    description: str,
    topics_type: type[topics_visitor.Topics],
    topic_apps: Iterable[topic_app.Topic],
) -> typer.Typer:
    """Create a new benchmark application."""
    topic_apps = list(topic_apps)
    if len(topic_apps) != len(topics_type):
        _LOGGER.critical(
            "Number of topic applications (%d) differs from number of topics (%d)",
            len(topic_apps),
            len(topics_type),
        )
        raise typer.Exit(1)
    app = typer.Typer(
        name=name,
        help=description,
        rich_markup_mode="rich",
    )
    #
    # Utilities
    #
    app.add_typer(
        help_app.new(topics_type),
        rich_help_panel=CommandCategories.UTILITIES,
    )
    app.command(rich_help_panel=CommandCategories.UTILITIES)(slurm_app.slurm_opts)
    #
    # Topics
    #
    for sub_app in topic_apps:
        app.add_typer(sub_app.app(), rich_help_panel=CommandCategories.TOPICS)
    return app


APP = typer.Typer(
    name="slurmbench",
    help="SLURM benchmark interface",
    rich_markup_mode="rich",
)
