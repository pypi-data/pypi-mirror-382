"""
Initialize a new DataDict project.
"""

import sys
from pathlib import Path
from typing import Optional

import click
from datadict_cli.lib.constants import PROJECT_FILE_NAME
from datadict_cli.util.common import console, print_error, print_success
from datadict_cli.util.logger import step


def init(name: Optional[str], yes: bool = False, verbose: bool = False):
    """
    Initialize a new DataDict project.

    Args:
        name: Project name (optional). If provided, creates a new directory.
              If None, initializes in current directory.
        yes: Skip confirmation prompts
        verbose: Enable verbose output
    """
    # Determine target directory
    if name:
        target_path = Path.cwd() / name
        project_name = name
    else:
        target_path = Path.cwd()
        project_name = target_path.name

    # Check if target directory already exists and has files
    if target_path.exists():
        if name:  # Creating a new directory
            if list(target_path.iterdir()):
                print_error(f"Directory '{name}' already exists and is not empty")
                sys.exit(1)
        else:  # Using current directory
            # Check if it already has a datadict_project.yml
            project_file = target_path / PROJECT_FILE_NAME
            if project_file.exists():
                print_error("DataDict project already exists in current directory")
                sys.exit(1)

    # Show confirmation message
    console.print("DataDict Init")
    console.print(f"Creating project '{project_name}' in {target_path}")

    if not yes:
        if not click.confirm("Continue?"):
            console.print("Cancelled.")
            sys.exit(0)

    # Create directory if needed
    if name:
        with step(f"Creating directory {target_path}"):
            target_path.mkdir(parents=True, exist_ok=True)

    # Create minimal datadict_project.yml
    project_content = f"""name: "{project_name}"
version: "1.0.0"
config-version: 1

catalogs: []
"""

    project_file = target_path / PROJECT_FILE_NAME
    with step(f"Writing {PROJECT_FILE_NAME}"):
        project_file.write_text(project_content)

    # Success message
    print_success("DataDict project initialized successfully!", f"Project: {project_name}")

    # Show next steps
    console.print("Next steps:")
    if name:
        console.print(f"  [cyan]cd {name}[/cyan]")
    console.print("  [cyan]# Add your catalogs to the project[/cyan]")
    console.print("  [cyan]datadict build[/cyan]")
