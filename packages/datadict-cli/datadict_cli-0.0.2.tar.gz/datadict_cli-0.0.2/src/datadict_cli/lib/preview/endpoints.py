from importlib import resources
from typing import Optional

from datadict_cli.lib.models import Catalog, Project
from datadict_cli.lib.queries import find_item
from datadict_cli.lib.serializer.api_schemas import (
    CatalogOut,
    ItemChildrenOut,
    ItemOut,
    ProjectOut,
)
from datadict_cli.lib.serializer.serializer import (
    serialize_catalog,
    serialize_children,
    serialize_item,
    serialize_project,
)
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="DataDict Preview API", openapi_url="/api/openapi.json")

_STATIC_PACKAGE = "datadict_cli.lib.preview.static"
_STATIC_ROOT = resources.files(_STATIC_PACKAGE)

app.mount(
    "/assets",
    StaticFiles(packages=[(_STATIC_PACKAGE, "assets")]),
    name="preview-assets",
)

# Global project instance - will be set by the preview server
_project: Optional[Project] = None


def set_project(project: Project):
    """Set the project instance"""
    global _project
    _project = project


def find_catalog_by_id(project: Project, catalog_id: str) -> Optional[Catalog]:
    """Find a catalog by its ID"""
    for catalog in project.catalogs:
        if catalog.id == catalog_id:
            return catalog
    return None


@app.get("/api/project", response_model=ProjectOut)
async def get_project() -> ProjectOut:
    """Get project overview from the active SQLite database."""
    if not _project:
        raise HTTPException(status_code=404, detail="Project not found")

    _, project_model = serialize_project(_project)
    return project_model


@app.get("/api/catalog/{catalog_id}", response_model=CatalogOut)
async def get_catalog(catalog_id: str) -> CatalogOut:
    """Get catalog details from the active SQLite database."""
    if not _project:
        raise HTTPException(status_code=404, detail="Project not found")

    catalog = find_catalog_by_id(_project, catalog_id)
    if not catalog:
        raise HTTPException(status_code=404, detail="Catalog not found")

    _, catalog_model = serialize_catalog(catalog, _project)
    return catalog_model


@app.get("/api/item/{item_id}", response_model=ItemOut)
async def get_item(item_id: str) -> ItemOut:
    """Get item details from the active SQLite database."""
    if not _project:
        raise HTTPException(status_code=404, detail="Project not found")

    item = find_item(_project, item_id, with_children=False)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    result = serialize_item(item)
    if not result:
        raise HTTPException(status_code=404, detail="Item cannot be serialized")

    _, item_model = result
    return item_model


@app.get("/api/children/{item_id}", response_model=ItemChildrenOut)
async def get_item_children(item_id: str) -> ItemChildrenOut:
    """Get item children from the active SQLite database."""
    if not _project:
        raise HTTPException(status_code=404, detail="Project not found")

    item = find_item(_project, item_id, with_children=True)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    result = serialize_children(item)
    if not result:
        raise HTTPException(status_code=404, detail="Item children cannot be serialized")

    _, children_model = result
    return children_model


@app.get("/api/health", include_in_schema=False)
async def health_check():
    """Simple API health check."""
    return {"msg": "DataDict Preview API", "status": "running"}


def _static_response(resource_path: str) -> FileResponse:
    """Return a FileResponse for the packaged static asset."""
    target = _STATIC_ROOT.joinpath(resource_path)
    if not target.is_file():
        raise FileNotFoundError(resource_path)

    with resources.as_file(target) as file_path:
        return FileResponse(file_path)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> FileResponse:
    """Serve the embedded favicon."""
    return _static_response("favicon.ico")


@app.get("/", include_in_schema=False)
async def serve_index() -> FileResponse:
    """Serve the SPA entrypoint."""
    return _static_response("index.html")


@app.get("/{full_path:path}", include_in_schema=False)
async def spa_fallback(full_path: str) -> FileResponse:
    """Serve asset files or fall back to the SPA entrypoint for unknown routes."""
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Endpoint not found")

    try:
        return _static_response(full_path)
    except FileNotFoundError:
        return _static_response("index.html")
