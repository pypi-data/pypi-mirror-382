import shutil
import time
from pathlib import Path

from datadict_cli.lib.project import load_project
from datadict_cli.util.common import (
    console,
    print_header,
    print_success,
)
from datadict_cli.util.logger import is_verbose, step


def build(project_path: Path, verbose: bool = False):
    """
    Build command implementation

    Loads the project from the specified path, refreshes the on-disk
    SQLite database, and copies it into the build/ directory for deployment.

    Args:
        project_path: Path to the DataDict project directory
        verbose: Enable verbose output showing all files and steps
    """
    build_path = project_path / "build"
    build_path.mkdir(parents=True, exist_ok=True)
    build_db_path = build_path / "datadict.db"

    # Show command header
    print_header("DataDict Build", project_path, build_db_path)

    # Step 1: Load project and refresh SQLite database
    with step("Loading project"):
        start_time = time.time()
        project = load_project(str(project_path))
        load_time = time.time() - start_time
    if is_verbose():
        console.print(
            f"Project: {project.project_name} v{project.version} - Catalogs: {len(project.catalogs)}"
        )

    if not project.db or project.db.path == ":memory:":
        raise RuntimeError(
            "Build requires a persistent SQLite database. Rerun without --in-memory-db."
        )

    source_db_path = Path(project.db.path)

    # Close the active connection before copying the file to avoid locking issues
    project.db.close()

    if not source_db_path.exists():
        raise FileNotFoundError(
            f"Project database not found at {source_db_path}. Did the load step succeed?"
        )

    # Step 2: Copy refreshed database into build directory
    with step("Exporting database"):
        start_time = time.time()
        if source_db_path.resolve() != build_db_path.resolve():
            if build_db_path.exists():
                build_db_path.unlink()
            shutil.copy2(source_db_path, build_db_path)
        export_time = time.time() - start_time

    total_time = load_time + export_time
    print_success("Build completed successfully!", f"Database: {build_db_path}")
    if is_verbose():
        console.print(f"Refresh time: {load_time:.2f}s")
        console.print(f"Copy time: {export_time:.2f}s")
        console.print(f"Total time: {total_time:.2f}s")
