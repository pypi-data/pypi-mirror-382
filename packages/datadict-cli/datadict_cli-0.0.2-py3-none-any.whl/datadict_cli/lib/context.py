"""Runtime context configuration for DataDict commands and library usage."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Optional

from pydantic import BaseModel


class DataDictContext(BaseModel):
    """Global runtime settings that drive DataDict behavior."""

    project_root: Optional[str] = None
    db_connection: str = ":memory:"
    skip_filesystem_load: bool = False


_current_context: DataDictContext | None = None


def set_datadict_context(context: DataDictContext) -> None:
    """Install the active DataDict context."""

    global _current_context
    _current_context = context


def get_datadict_context() -> DataDictContext:
    """Return the active DataDict context.

    Raises:
        RuntimeError: If no context has been configured.
    """

    if _current_context is None:
        raise RuntimeError("DataDict context has not been initialised")
    return _current_context


def reset_datadict_context() -> None:
    """Clear the active DataDict context (primarily for tests)."""

    global _current_context
    _current_context = None


@contextmanager
def datadict_context(
    *,
    project_root: Optional[str] = None,
    db_connection: str = ":memory:",
    skip_filesystem_load: bool = False,
) -> Iterator[None]:
    """Context manager to install a temporary DataDict context."""

    set_datadict_context(
        DataDictContext(
            project_root=project_root,
            db_connection=db_connection,
            skip_filesystem_load=skip_filesystem_load,
        )
    )
    try:
        yield
    finally:
        reset_datadict_context()
