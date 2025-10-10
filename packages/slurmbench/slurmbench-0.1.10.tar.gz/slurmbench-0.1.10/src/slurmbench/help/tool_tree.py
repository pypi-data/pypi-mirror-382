"""Tool tree helping module."""


# Due to typer usage:

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import slurmbench.topics.visitor as topics_visitor


def tool_tree(topics_type: type[topics_visitor.Topics]) -> str:
    """Tool tree command."""
    md_string = (
        "# Tool tree\n"
        "\n"
        "Topics are at the first level, and tools are at the second level.\n"
        "The commands are under parenthesis.\n"
        "\n"
    )

    for topic in topics_type:
        topic_description = topic.to_description()
        tools = topic.tools()
        md_string += f"* {topic_description.name()} ({topic_description.cmd()})\n"
        for tool in tools:
            tool_description = tool.to_description()
            md_string += f"  * {tool_description.name()} ({tool_description.cmd()})\n"

    return md_string
