from pathlib import Path
from typing import TYPE_CHECKING, Optional

from datadict_cli.lib.context import DataDictContext, get_datadict_context, set_datadict_context
from datadict_cli.lib.lineage import sync_project_lineage
from datadict_cli.lib.loader import load_catalog
from datadict_cli.lib.models import Catalog, Project
from datadict_cli.lib.schemas import ProjectConfig
from datadict_cli.lib.types import CatalogType
from datadict_cli.util.db import DB, default_project_db_path
from ruamel.yaml import YAML

if TYPE_CHECKING:
    pass


def _ensure_context(project_path: str) -> DataDictContext:
    try:
        return get_datadict_context()
    except RuntimeError:
        context = DataDictContext(
            project_root=project_path,
            db_connection=default_project_db_path(project_path),
            skip_filesystem_load=False,
        )
        set_datadict_context(context)
        return context


def load_project(path: str) -> Project:
    """Load a project according to the active DataDict context."""

    context = _ensure_context(path)
    project_root = Path(context.project_root or path)

    db = DB(db_path=context.db_connection)

    if context.skip_filesystem_load:
        return _hydrate_project_from_db(db, project_root)

    project_file = project_root / "datadict_project.yml"
    if not project_file.exists():
        raise FileNotFoundError(f"Project file not found: {project_file}")

    yaml = YAML(typ="safe")
    with open(project_file, "r") as f:
        project_data = yaml.load(f)

    project_config = ProjectConfig(**project_data)  # type: ignore

    db.reset_model_state()

    project = Project(
        project_name=project_config.name,
        version=project_config.version,
        path=str(project_root),
        db=db,
        catalogs=[],
    )

    db.upsert_project_metadata(
        name=project.project_name,
        version=project.version,
    )

    for catalog_name in project_config.catalogs:
        catalog_path = project_root / catalog_name
        if catalog_path.exists():
            catalog = load_catalog(project, catalog_name, str(catalog_path))
            project.catalogs.append(catalog)

    # Rebuild resolved lineage after all catalogs are loaded
    sync_project_lineage(project)

    return project


def load_project_from_db(db_path: str, project_root: Optional[str] = None) -> Project:
    """Load a project using only the persisted SQLite database."""

    db = DB(db_path=db_path)
    root_path = Path(project_root) if project_root else None
    return _hydrate_project_from_db(db, root_path)


def _hydrate_project_from_db(db: DB, project_root: Optional[Path]) -> Project:
    metadata = db.fetchone("SELECT name, version FROM project_metadata WHERE id = 1")
    if metadata is None:
        raise ValueError("Project metadata not found in database")

    project = Project(
        project_name=metadata["name"],
        version=metadata["version"],
        path=str(project_root) if project_root else None,
        db=db,
        catalogs=[],
    )

    catalogs = db.fetchall("SELECT id, name, type, path FROM catalogs ORDER BY name")
    for catalog_row in catalogs:
        catalog_type_value = catalog_row["type"] or CatalogType.DATABASE.value
        catalog = Catalog(
            id=catalog_row["id"],
            name=catalog_row["name"],
            type=CatalogType(catalog_type_value),
            path=catalog_row["path"],
        )
        catalog.set_project(project)
        project.catalogs.append(catalog)

    sync_project_lineage(project)

    return project
