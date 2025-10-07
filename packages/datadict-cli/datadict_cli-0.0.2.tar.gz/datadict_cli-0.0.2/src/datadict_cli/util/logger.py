"""
Simple, consistent logging for the CLI and libraries.

Goals:
- One-line messages (no progress bars/spinners)
- Sensible colors when appropriate
- Global verbose toggle without prop drilling
- Bridge stdlib logging to our console style
"""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator, Optional

from rich.console import Console

# Global console configured once; keep highlight off for cleaner logs
console = Console(highlight=False)


@dataclass
class LoggerConfig:
    verbose: bool = False
    colors: Optional[bool] = None  # None -> auto (based on terminal)


_config = LoggerConfig()
_handler_attached = False


class _RichLineHandler(logging.Handler):
    """A logging handler that prints single-line messages with simple colors."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
        except Exception:  # pragma: no cover - defensive
            msg = record.getMessage()

        level = record.levelno
        if level >= logging.ERROR:
            console.print(f"[red]ERROR:[/red] {msg}")
        elif level >= logging.WARNING:
            console.print(f"[yellow]WARN:[/yellow] {msg}")
        elif level >= logging.INFO:
            console.print(msg)
        else:  # DEBUG
            # Dim debug for readability
            console.print(f"[dim]{msg}[/dim]")


def init_logging(verbose: bool = False, colors: Optional[bool] = None) -> None:
    """Initialize global logging configuration.

    - Sets global verbose flag
    - Configures root logger to use our Rich handler
    - Routes library logs (logging.getLogger(__name__)) through our format
    """
    global _handler_attached
    _config.verbose = bool(verbose)
    _config.colors = colors

    # Configure Rich console color policy
    if colors is not None:
        console.no_color = not bool(colors)
    else:
        # Auto based on terminal capability
        console.no_color = False

    root = logging.getLogger()
    # Default to WARNING when not verbose to keep output minimal.
    root.setLevel(logging.DEBUG if _config.verbose else logging.WARNING)

    if not _handler_attached:
        # Remove default handlers to avoid duplicate output
        for h in list(root.handlers):
            root.removeHandler(h)

        handler = _RichLineHandler()
        # Use a minimal formatter: just the message. Libraries provide context in message.
        handler.setFormatter(logging.Formatter("%(message)s"))
        root.addHandler(handler)
        _handler_attached = True


def is_verbose() -> bool:
    return _config.verbose


@contextmanager
def step(description: str, show_duration_in_verbose: bool = True) -> Iterator[None]:
    """Context manager for classical one-line steps.

    Usage:
        with step("Loading catalog my_catalog"):
            ...
        # -> "Loading catalog my_catalog... Done (0.23s)" in verbose mode
    """
    start = time.perf_counter()
    try:
        yield
    except Exception as e:
        console.print(f"{description}... [red]Failed[/red]: {e}")
        raise
    else:
        suffix = ""
        if _config.verbose and show_duration_in_verbose:
            elapsed = time.perf_counter() - start
            suffix = f" ({elapsed:.2f}s)"
        console.print(f"{description}... [green]Done[/green]{suffix}")
