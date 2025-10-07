"""
File to start and manage the preview server
"""

import uvicorn
from datadict_cli.lib.preview.endpoints import app, set_project
from datadict_cli.lib.project import load_project


def start_preview_server(project_path: str, host: str = "127.0.0.1", port: int = 8000):
    """
    Load project and start the preview server

    Args:
        project_path: Path to the DataDict project directory
        host: Host to bind the server to
        port: Port to bind the server to
    """
    # Load the project (same as build command)
    project = load_project(project_path)

    # Set the project in the endpoints module
    set_project(project)

    print(f"Starting DataDict preview server at http://{host}:{port}")
    print(f"Project: {project.project_name} v{project.version}")
    print(f"Catalogs: {len(project.catalogs)}")

    # Start the server
    uvicorn.run(app, host=host, port=port)
