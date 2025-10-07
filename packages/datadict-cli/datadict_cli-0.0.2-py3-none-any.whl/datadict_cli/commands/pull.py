"""
DataDict pull command implementation.

Synchronizes local catalogs with their remote data sources by pulling
metadata and applying changes to the filesystem.

Usage:
    datadict pull <catalog_name>     # Pull a specific catalog
    datadict pull --all-catalogs     # Pull all catalogs in project
    datadict pull <catalog> --force  # Force pull even if no changes detected
"""

from pathlib import Path
from typing import Optional

from datadict_cli.lib.catalog import reconcile_catalog
from datadict_cli.lib.project import load_project
from datadict_cli.util.common import (
    console,
    print_error,
    print_header,
)
from datadict_cli.util.logger import is_verbose, step


def pull(
    project_path: Path,
    catalog_name: Optional[str] = None,
    all_catalogs: bool = False,
    target: Optional[str] = None,
    force: bool = False,
    verbose: bool = False,
):
    """
    Pull command implementation.

    Synchronizes local catalog metadata with remote data sources by:
    1. Loading the project and catalogs
    2. Connecting to remote data sources using configured profiles
    3. Comparing remote metadata with local state
    4. Applying required changes to filesystem (create, modify, archive)

    Args:
        project_path: Path to the DataDict project directory
        catalog_name: Name of specific catalog to pull (mutually exclusive with all_catalogs)
        all_catalogs: Pull all catalogs in the project (mutually exclusive with catalog_name)
        target: Target name for credential lookup (uses profile default if None)
        force: Force pull operation even if no changes are detected
        verbose: Enable verbose output showing detailed processing steps

    Raises:
        ValueError: If neither catalog_name nor all_catalogs is specified, or both are specified
        FileNotFoundError: If specified catalog doesn't exist
        Exception: For connection or sync errors
    """
    # Validate arguments
    if not catalog_name and not all_catalogs:
        raise ValueError("Must specify either a catalog name or --all-catalogs")

    if catalog_name and all_catalogs:
        raise ValueError("Cannot specify both catalog name and --all-catalogs")

    # Show command header
    if all_catalogs:
        operation = "Pull All Catalogs"
    else:
        operation = f"Pull Catalog: {catalog_name}"

    print_header(f"DataDict {operation}", project_path, None)

    # Step 1: Load project
    with step("Loading project"):
        project = load_project(str(project_path))
    if is_verbose():
        console.print(
            f"Project: {project.project_name} v{project.version} - Catalogs: {len(project.catalogs)}"
        )

    # Step 2: Determine catalogs to pull
    catalogs_to_pull = []

    if all_catalogs:
        catalogs_to_pull = project.catalogs
        if not catalogs_to_pull:
            print_error("No catalogs found in project")
            return
    else:
        # Find specific catalog
        catalog_found = None
        for catalog in project.catalogs:
            if catalog.name == catalog_name:
                catalog_found = catalog
                break

        if not catalog_found:
            available_catalogs = [c.name for c in project.catalogs]
            raise FileNotFoundError(
                f"Catalog '{catalog_name}' not found. Available catalogs: {', '.join(available_catalogs)}"
            )

        catalogs_to_pull = [catalog_found]

    # Step 3: Pull each catalog
    total_catalogs = len(catalogs_to_pull)
    success_count = 0
    error_count = 0

    for i, catalog in enumerate(catalogs_to_pull, 1):
        try:
            result = None
            with step(f"Pulling catalog {i}/{total_catalogs}: {catalog.name}"):
                result = reconcile_catalog(catalog, target)
            success_count += 1
            if result is not None:
                console.print(f"  Changes: {result.total_changes}, Errors: {result.error_count}")
        except Exception:
            error_count += 1
            # Defer raising until after summary so users see progress

    # Step 4: Show summary
    # Final summary (same format whether single or multiple catalogs)
    console.print(
        f"Summary: pulled {success_count}/{total_catalogs} catalog(s); errors: {error_count}"
    )

    # Exit with an error if any catalog failed
    if error_count > 0:
        raise RuntimeError("Pull finished with errors; see above for details")
