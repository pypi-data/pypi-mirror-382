"""
Catalog management commands.
"""

import sys
from pathlib import Path

from datadict_cli.lib.constants import CATALOG_FILE_NAME, PROJECT_FILE_NAME
from datadict_cli.lib.schemas import ProjectConfig
from datadict_cli.lib.types import CatalogType
from datadict_cli.util.common import console, print_error, print_success
from datadict_cli.util.logger import step
from ruamel.yaml import YAML


def add_catalog(
    name: str,
    catalog_type: CatalogType = CatalogType.DATABASE,
    profile: str = "myprofile",
    verbose: bool = False,
):
    """
    Add a new catalog to the DataDict project.

    Args:
        name: Name of the catalog to create
        catalog_type: Type of catalog (default: database)
        profile: Profile name for connections (default: myprofile)
        verbose: Enable verbose output
    """
    project_path = Path.cwd()
    project_file = project_path / PROJECT_FILE_NAME

    # Check if we're in a DataDict project
    if not project_file.exists():
        print_error("Not in a DataDict project directory", "Run 'datadict init' first")
        sys.exit(1)

    # Check if catalog directory already exists
    catalog_path = project_path / name
    if catalog_path.exists():
        print_error(f"Catalog directory '{name}' already exists")
        sys.exit(1)

    if verbose:
        console.print("Adding Catalog")
        console.print(f"Name: {name} | Type: {catalog_type} | Profile: {profile}")

    # Load current project configuration
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096

    with open(project_file, "r") as f:
        project_data = yaml.load(f)

    # Validate project structure
    try:
        if not project_data:
            raise ValueError("Project file is empty")
        # Ensure required fields exist
        if "name" not in project_data:
            raise ValueError("Project configuration missing required field: name")
        if "version" not in project_data:
            raise ValueError("Project configuration missing required field: version")
        # Type checker needs explicit field access
        project_config = ProjectConfig(
            name=project_data["name"],
            version=project_data["version"],
            catalogs=project_data.get("catalogs", []),
        )
    except Exception as e:
        print_error(f"Invalid project configuration: {e}")
        sys.exit(1)

    # Check if catalog already exists in project
    if name in project_config.catalogs:
        print_error(f"Catalog '{name}' already exists in project configuration")
        sys.exit(1)

    # Create catalog directory
    with step(f"Creating directory {catalog_path}"):
        catalog_path.mkdir(parents=True, exist_ok=True)

    # Create catalog.yml file
    catalog_config_content = f"""name: "{name}"
type: "{catalog_type.value}"

connection:
  profile: "{profile}"

# Default directory structure:
# "database/schema/table.yml"
"""

    catalog_file = catalog_path / CATALOG_FILE_NAME
    with step(f"Writing {CATALOG_FILE_NAME}"):
        catalog_file.write_text(catalog_config_content)

    # Add catalog to project configuration
    project_data["catalogs"].append(name)

    # Write updated project file
    with step(f"Updating {PROJECT_FILE_NAME}"):
        with open(project_file, "w") as f:
            yaml.dump(project_data, f)

    # Success message
    print_success(f"Catalog '{name}' added successfully!", f"Directory created at: {catalog_path}")

    # Show next steps
    console.print("\n[bold]Next steps:[/bold]")
    console.print(f"  [cyan]cd {name}[/cyan]")
    console.print("  [cyan]# Add your table definitions[/cyan]")
    console.print("  [cyan]datadict build[/cyan]")
