"""
Info command implementation.

Shows information about a DataDict project including catalogs, items, and structure.
"""

import time
from pathlib import Path

from datadict_cli.lib.project import load_project
from datadict_cli.lib.queries import find_catalog_items
from datadict_cli.util.common import (
    console,
    print_header,
    print_success,
)
from datadict_cli.util.logger import is_verbose, step


def info(project_path: Path, verbose: bool = False):
    """
    Info command implementation

    Shows detailed information about the DataDict project.

    Args:
        project_path: Path to the DataDict project directory
        verbose: Enable verbose output showing detailed information
    """
    # Show command header
    print_header("DataDict Project Info", project_path)

    # Step 1: Load project
    with step("Loading project"):
        start_time = time.time()
        project = load_project(str(project_path))
        time.time() - start_time

    # Display project information
    console.print(
        f"Project: {project.project_name}  Version: {project.version}  Catalogs: {len(project.catalogs)}"
    )

    total_items = 0
    for catalog in project.catalogs:
        # Compute per-catalog info
        root_items = find_catalog_items(project, catalog.id)
        catalog_items = len(catalog.items)
        total_items += catalog_items
        console.print(
            f"- {catalog.name} ({catalog.type})  items={catalog_items}  roots={len(root_items)}"
        )
        if is_verbose() and root_items:
            for item in root_items[:5]:
                console.print(f"  • {item.name} ({item.type})")
            if len(root_items) > 5:
                console.print(f"  … and {len(root_items) - 5} more")

    if project.catalogs:
        console.print(f"Total items across all catalogs: {total_items}")

    print_success("Project analysis complete!")
