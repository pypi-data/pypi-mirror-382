"""Tools environment logic.

Some tools require a specific environment,
such as a specific virtualenv, setting binary paths etc.

This module provides such logic.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

_LOGGER = logging.getLogger(__name__)


class MissingMagicCommentError:
    """Missing magic comment error."""

    def __init__(self, script_path: Path, magic_comment: str) -> None:
        self._script_path = script_path
        self._magic_comment = magic_comment

    def script_path(self) -> Path:
        """Get the script path."""
        return self._script_path

    def magic_comment(self) -> str:
        """Get the magic comment."""
        return self._magic_comment

    def __str__(self) -> str:
        """Get string representation."""
        return (
            f"Missing magic comment `{self._magic_comment}`"
            f" in script `{self._script_path}`"
        )


class ScriptWrapper:
    """Wrapper to run a bash script in a specific environment."""

    BEGIN_ENV_MAGIC_COMMENT = "# PBFBENCH BEGIN_ENV"
    MID_ENV_MAGIC_COMMENT = "# PBFBENCH MID_ENV"
    END_ENV_MAGIC_COMMENT = "# PBFBENCH END_ENV"

    @classmethod
    def new(cls, script_path: Path) -> Self | MissingMagicCommentError:
        """Create a new environment wrapper."""
        match indices_or_err := cls._index_script(script_path):
            case MissingMagicCommentError():
                return indices_or_err
            case _:
                return cls(script_path, *indices_or_err)

    @classmethod
    def _index_script(
        cls,
        script_path: Path,
    ) -> tuple[int, int, int] | MissingMagicCommentError:
        """Index the script lines."""

        def _index_line_iter(script_path: Path) -> Iterator[tuple[int, str] | None]:
            """Iterate over the script lines."""
            with script_path.open("r") as f_in_script:
                line = next(f_in_script, None)
                k = 0
                while line is not None:
                    yield (k, line)
                    line = next(f_in_script, None)
                    k += 1
                yield None

        def _find_magic_comment(
            index_line_iter: Iterator[tuple[int, str] | None],
            magic_comment: str,
        ) -> int | MissingMagicCommentError:
            """Find magic comment or return error."""
            index_line = next(index_line_iter)
            while index_line is not None and not index_line[1].startswith(
                magic_comment,
            ):
                index_line = next(index_line_iter)
            if index_line is None:
                return MissingMagicCommentError(script_path, magic_comment)
            return index_line[0]

        index_line_iter = _index_line_iter(script_path)
        indices = []
        for magic_comment in (
            cls.BEGIN_ENV_MAGIC_COMMENT,
            cls.MID_ENV_MAGIC_COMMENT,
            cls.END_ENV_MAGIC_COMMENT,
        ):
            match index := _find_magic_comment(index_line_iter, magic_comment):
                case MissingMagicCommentError():
                    return index
                case int():
                    indices.append(index)
        return (indices[0], indices[1], indices[2])

    def __init__(
        self,
        script_path: Path,
        begin_line_index: int,
        mid_line_index: int,
        end_line_index: int,
    ) -> None:
        self.__script_path = script_path
        self.__begin_line_index = begin_line_index
        self.__mid_line_index = mid_line_index
        self.__end_line_index = end_line_index

    def init_env_lines(self) -> Iterator[str]:
        """Iterate over the script lines that init the environment."""
        with self.__script_path.open("r") as f_in_script:
            iter_lines = iter(f_in_script)
            line = next(iter_lines)
            k = 0
            # Skip before the begin magic comment
            while k < self.__begin_line_index:
                line = next(iter_lines)
                k += 1
            # Yield the lines until the mid magic comment
            while k < self.__mid_line_index:
                yield line.rstrip()
                line = next(iter_lines)
                k += 1
            # Add the mid magic comment
            yield line.rstrip()

    def close_env_lines(self) -> Iterator[str]:
        """Iterate over the script lines that close the environment."""
        with self.__script_path.open("r") as f_in_script:
            iter_lines = iter(f_in_script)
            line = next(iter_lines)
            k = 0
            # Skip before the mid magic comment
            while k < self.__mid_line_index:
                line = next(iter_lines)
                k += 1
            # Yield the lines until the end magic comment
            while k < self.__end_line_index:
                yield line.rstrip()
                line = next(iter_lines)
                k += 1
            # Add the end magic comment
            yield line.rstrip()
