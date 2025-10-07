"""
Common CLI utilities and decorators for DataDict commands.

Provides reusable components for consistent CLI experience across all commands.
"""

import functools
from pathlib import Path
from typing import Any, Callable

import click
from datadict_cli.lib.context import DataDictContext, reset_datadict_context, set_datadict_context
from datadict_cli.util.db import default_project_db_path
from datadict_cli.util.logger import (
    console,
    init_logging,
)
from rich.tree import Tree

# Keep a module-level console reference from util.logger for consistent output
# (util.logger configures colors and verbosity globally)


def common_options(func: Callable) -> Callable:
    """
    Decorator that adds common CLI options to commands.

    Adds:
    - --path: Project directory path (defaults to current directory)
    - --verbose/-v: Enable verbose output
    - --yes/-y: Assume yes to all prompts

    Usage:
        @common_options
        def my_command(path: Path, verbose: bool, yes: bool, **kwargs):
            pass
    """

    @click.option(
        "--path",
        type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
        default=None,
        help="Path to the DataDict project directory (defaults to current directory)",
    )
    @click.option(
        "--verbose",
        "-v",
        is_flag=True,
        help="Enable verbose output showing detailed processing steps",
    )
    @click.option(
        "--yes",
        "-y",
        is_flag=True,
        help="Assume yes to all prompts",
    )
    @click.option(
        "--in-memory-db",
        is_flag=True,
        help="Use an in-memory SQLite database instead of persisting to disk",
    )
    @click.option(
        "--skip-load",
        is_flag=True,
        help="Skip filesystem loading and rely on the existing SQLite database",
    )
    @functools.wraps(func)
    def wrapper(
        path: Path | None,
        verbose: bool,
        yes: bool,
        in_memory_db: bool,
        skip_load: bool,
        *args,
        **kwargs,
    ):
        # Initialize global logging/verbosity once per command invocation
        init_logging(verbose)

        # Use current directory if no path specified
        project_path = path or Path.cwd()

        db_connection = ":memory:" if in_memory_db else default_project_db_path(str(project_path))

        set_datadict_context(
            DataDictContext(
                project_root=str(project_path),
                db_connection=db_connection,
                skip_filesystem_load=skip_load,
            )
        )
        try:
            return func(project_path, verbose, yes, *args, **kwargs)
        finally:
            reset_datadict_context()

    return wrapper


class CLIProgress:
    """
    Lightweight progress context that avoids spinners/bars.

    Maintains API compatibility with previous Rich-based progress usage,
    but intentionally prints nothing on updates to keep output to one line per step.
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.console = console  # Expose console for use by commands
        self._tasks: dict[int, dict[str, Any]] = {}
        self._next_id = 1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False  # do not suppress exceptions

    def add_task(self, description: str, total: int = 1):
        task_id = self._next_id
        self._next_id += 1
        # Store raw description; caller controls user-facing messages separately
        self._tasks[task_id] = {
            "description": description,
            "total": total,
            "completed": 0,
        }
        return task_id

    def update_task(self, task_id: int, completed: int | None = None, **kwargs):
        task = self._tasks.get(task_id)
        if not task:
            return
        if completed is not None:
            task["completed"] = completed
        task.update(kwargs)


def print_header(title: str, project_path: Path, output_path: Path | None = None):
    """Print a compact command header (one or two lines)."""
    console.print(f"{title}")
    console.print(
        f"Project: {project_path}" + (f"  -> Output: {output_path}" if output_path else "")
    )


def print_success(message: str, details: str = ""):
    """Print a success message as a single concise line, no OK: prefix."""
    suffix = f" - {details}" if details else ""
    console.print(f"{message}{suffix}")


def print_error(message: str, details: str = ""):
    """Print an error message as a single concise line."""
    suffix = f" - {details}" if details else ""
    console.print(f"[red]ERROR:[/red] {message}{suffix}")


def print_step_success(message: str, verbose_details: str = "", verbose: bool = False):
    """Print a step completion message as a single line."""
    details = f" - {verbose_details}" if verbose and verbose_details else ""
    # Keep markup from callers (they sometimes pass [bold] etc.), but end with Done
    console.print(f"{message}... [green]Done[/green]{details}")


def print_step_error(message: str):
    """Print a step error message as a single line."""
    console.print(f"{message}... [red]Failed[/red]")


def create_tree(title: str) -> Tree:
    """Create a Rich tree with consistent styling."""
    return Tree(f"[bold]{title}[/bold]")


def print_file_list(title: str, files: list[str], project_path: Path):
    """Print a formatted list of files."""
    if not files:
        return

    console.print(f"\n[bold]{title}:[/bold]")
    for file_path in sorted(files):
        rel_path = Path(file_path).relative_to(project_path)
        console.print(f"  [green]•[/green] {rel_path}")
