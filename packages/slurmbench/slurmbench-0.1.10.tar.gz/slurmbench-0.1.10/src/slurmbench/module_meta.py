"""Meta logic on module."""

from pathlib import Path

from .tool import description as desc
from .topic import description as topic_desc

PBFBENCH_ROOT = Path(__file__).parent

TOPICS_MODULE_NAME = "topics"


def topic_module_path(topic_name: str) -> Path:
    """Get topic module path."""
    return PBFBENCH_ROOT / TOPICS_MODULE_NAME / topic_name.lower()


def topic_module_path_from_description(topic: topic_desc.Description) -> Path:
    """Get topic module path."""
    return topic_module_path(topic.name())


def tool_module_path(topic_name: str, tool_name: str) -> Path:
    """Get tool module path."""
    return topic_module_path(topic_name) / tool_name.lower()


def tool_module_path_from_descriptions(
    topic: topic_desc.Description,
    tool: desc.Description,
) -> Path:
    """Get tool module path."""
    return tool_module_path(topic.name(), tool.name())


def path_to_python_path(path: Path) -> str:
    """Get python path."""
    return str(path).replace("/", ".")
