#!/usr/bin/env python3
"""
DataDict CLI - Main entry point for the DataDict command line interface.
"""

import sys
from pathlib import Path

import click
from datadict_cli.commands.build import build as build_command
from datadict_cli.commands.catalog import add_catalog
from datadict_cli.commands.info import info as info_command
from datadict_cli.commands.init import init as init_command
from datadict_cli.commands.preview import preview as preview_command
from datadict_cli.commands.pull import pull as pull_command
from datadict_cli.lib.types import CatalogType
from datadict_cli.util.common import common_options, print_error
from datadict_cli.util.logger import init_logging


@click.group()
@click.version_option()
def cli():
    """
    DataDict - Data catalog management tool

    Manage your data catalogs through YAML files and generate
    beautiful documentation sites.
    """
    pass


@cli.command()
@click.argument("name", required=False)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Assume yes to all prompts",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output showing detailed processing steps",
)
def init(name: str | None, yes: bool, verbose: bool):
    """
    Initialize a new DataDict project.

    If NAME is provided, creates a new directory with that name.
    If no NAME is provided, initializes in the current directory.
    """
    init_logging(verbose)

    try:
        init_command(name, yes=yes, verbose=verbose)
    except Exception as e:
        details = "Use --verbose for more details" if not verbose else ""
        print_error(str(e), details)
        sys.exit(1)


@cli.command()
@common_options
def build(project_path: Path, verbose: bool, yes: bool):
    """
    Build the DataDict project SQLite database.

    Loads the project configuration and catalogs, refreshes the
    project SQLite database, and exports a copy to `build/datadict.db`.
    """
    try:
        build_command(project_path, verbose=verbose)
    except Exception as e:
        details = "Use --verbose for more details" if not verbose else ""
        print_error(str(e), details)
        sys.exit(1)


@cli.command()
@common_options
def info(project_path: Path, verbose: bool, yes: bool):
    """
    Show information about the DataDict project.

    Displays project metadata, catalog details, and item counts.
    """
    try:
        info_command(project_path, verbose=verbose)
    except Exception as e:
        details = "Use --verbose for more details" if not verbose else ""
        print_error(str(e), details)
        sys.exit(1)


@cli.command()
@common_options
@click.option(
    "--host",
    default="127.0.0.1",
    help="Host to bind the server to (default: 127.0.0.1)",
)
@click.option(
    "--port",
    "-p",
    default=8000,
    type=int,
    help="Port to bind the server to (default: 8000)",
)
def preview(project_path: Path, verbose: bool, yes: bool, host: str, port: int):
    """
    Start a preview server for the DataDict project.

    Loads the project and serves the same JSON content as the build system
    via HTTP API endpoints. The frontend can seamlessly switch between
    static build files and the live preview server.

    API Endpoints:
      /api/project        - Project overview
      /api/catalog/{uuid} - Catalog details
      /api/item/{uuid}    - Item details
    """
    try:
        preview_command(project_path, host=host, port=port, verbose=verbose)
    except Exception as e:
        details = "Use --verbose for more details" if not verbose else ""
        print_error(str(e), details)
        sys.exit(1)


@cli.group()
def catalog():
    """
    Manage data catalogs in the DataDict project.

    Commands for adding, listing, and managing catalogs.
    """
    pass


@catalog.command("add")
@click.argument("name")
@click.option(
    "--type",
    "catalog_type",
    default="database",
    type=click.Choice(["database"], case_sensitive=False),
    help="Type of catalog to create (default: database)",
)
@click.option(
    "--profile",
    default="myprofile",
    help="Profile name for connections (default: myprofile)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output showing detailed processing steps",
)
def catalog_add(name: str, catalog_type: str, profile: str, verbose: bool):
    """
    Add a new catalog to the DataDict project.

    Creates a new catalog directory and adds it to the project configuration.
    The catalog directory will contain a catalog.yml file with the specified
    type and profile configuration.

    Example:
        datadict catalog add my_postgres --type=database --profile=prod_db
    """
    init_logging(verbose)

    try:
        # Convert string to enum
        catalog_type_enum = CatalogType(catalog_type.lower())
        add_catalog(name, catalog_type=catalog_type_enum, profile=profile, verbose=verbose)
    except Exception as e:
        details = "Use --verbose for more details" if not verbose else ""
        print_error(str(e), details)
        sys.exit(1)


@cli.command()
@click.argument("catalog_name", required=False)
@click.option(
    "--all-catalogs",
    is_flag=True,
    help="Pull all catalogs in the project",
)
@click.option(
    "--target",
    "-t",
    help="Target name for credential lookup (uses profile default if not specified)",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force pull operation even if no changes are detected",
)
@common_options
def pull(
    project_path: Path,
    verbose: bool,
    yes: bool,
    catalog_name: str | None,
    all_catalogs: bool,
    target: str | None,
    force: bool,
):
    """
    Synchronize local catalogs with remote data sources.

    Connects to configured remote data sources (databases, APIs, etc.) and
    pulls the latest metadata, then applies any changes to the local YAML
    files while preserving human-added documentation.

    You must specify either a CATALOG_NAME or use --all-catalogs:

    \b
    Examples:
        datadict pull my_postgres              # Pull specific catalog
        datadict pull --all-catalogs          # Pull all catalogs
        datadict pull my_db --target=prod     # Use specific target
        datadict pull my_db --force           # Force sync even if no changes

    The pull operation will:
    1. Load connection credentials from profiles.yml
    2. Connect to the remote data source
    3. Compare remote metadata with local state
    4. Apply changes (create, modify, archive items)
    5. Preserve existing descriptions and notes
    """
    try:
        pull_command(
            catalog_name=catalog_name,
            all_catalogs=all_catalogs,
            target=target,
            force=force,
            project_path=project_path,
            verbose=verbose,
        )
    except Exception as e:
        details = "Use --verbose for more details" if not verbose else ""
        print_error(str(e), details)
        sys.exit(1)


if __name__ == "__main__":
    cli()
