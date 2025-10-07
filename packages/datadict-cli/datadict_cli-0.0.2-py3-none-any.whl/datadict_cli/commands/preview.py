"""
Preview command implementation

Starts a local HTTP server that serves project metadata straight from the
in-memory models backed by the SQLite database.
"""

import signal
import sys
import traceback
from pathlib import Path

from datadict_cli.lib.preview.server import start_preview_server
from datadict_cli.util.common import console, print_error, print_header, print_success


def preview(project_path: Path, host: str = "127.0.0.1", port: int = 8000, verbose: bool = False):
    """
    Preview command implementation

    Loads the project and starts a local HTTP server that serves the same
    metadata stored in the project SQLite database.

    Args:
        project_path: Path to the DataDict project directory
        host: Host to bind the server to
        port: Port to bind the server to
        verbose: Enable verbose output
    """
    print_header("DataDict Preview Server", project_path)

    # This blocks until interrupted; print a single line for startup
    if verbose:
        console.print(f"Starting server on {host}:{port}")

    try:
        # Set up signal handler for graceful shutdown
        def signal_handler(sig, frame):
            print("\n")
            print_success("Preview server stopped")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start the preview server (this will block)
        console.print(f"Starting preview server at http://{host}:{port}")
        start_preview_server(str(project_path), host=host, port=port)

    except KeyboardInterrupt:
        print("\n")
        print_success("Preview server stopped")
    except Exception as e:
        print_error(f"Failed to start preview server: {str(e)}")
        if verbose:
            traceback.print_exc()
        raise
