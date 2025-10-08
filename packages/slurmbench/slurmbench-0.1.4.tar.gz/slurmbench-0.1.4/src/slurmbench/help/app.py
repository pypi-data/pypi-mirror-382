"""Help application."""

# Due to typer usage:
# ruff: noqa: FBT002

import logging
from pathlib import Path
from typing import Annotated

import typer
from rich.markdown import Markdown as Md

import slurmbench.help.tool_tree as help_tool_tree
import slurmbench.topics.visitor as topics_visitor
from slurmbench import root_logging

_LOGGER = logging.getLogger(__name__)


def new(topics_type: type[topics_visitor.Topics]) -> typer.Typer:
    """Create a new help application."""
    app = typer.Typer(name="help", help="Help commands", rich_markup_mode="rich")
    tool_tree_app = ToolTree(topics_type)
    app.command(name=tool_tree_app.NAME, help=tool_tree_app.help())(
        tool_tree_app.main,
    )
    return app


class ToolTree[T: type[topics_visitor.Topics]]:
    """Help application."""

    class Opts:
        """Tool tree options."""

        MARKDOWN = typer.Argument(help="Markdown file")

    NAME = "tool-tree"

    def __init__(self, topics_type: T) -> None:
        """Initialize."""
        self._topics_type = topics_type

    def topics_type(self) -> T:
        """Get topics type."""
        return self._topics_type

    def main(
        self,
        markdown_file: Annotated[Path | None, Opts.MARKDOWN] = None,
        debug: Annotated[bool, root_logging.OPT_DEBUG] = False,
    ) -> None:
        """Generate the tree of available tools."""
        root_logging.init_logger(_LOGGER, "Running tool tree helper", debug)
        md_str = help_tool_tree.tool_tree(self.topics_type())

        root_logging.CONSOLE.print(Md(md_str))

        if markdown_file is not None:
            _LOGGER.info("Saving markdown file to `%s`", markdown_file)
            with markdown_file.open("w") as f_out:
                f_out.write(md_str)

    def help(self) -> str:
        """Get help."""
        return "Generate the tree of available tools"
