# Catalog loader
from pathlib import Path
from typing import Dict, List, Optional

from datadict_cli.lib.models import Catalog, Item, Project, generate_deterministic_id
from datadict_cli.lib.queries import insert_catalog, insert_item
from datadict_cli.lib.schemas import CatalogConfig
from datadict_cli.lib.types import CatalogType
from datadict_connector_base import CatalogItem
from ruamel.yaml import YAML


class CatalogLoader:
    """
    Wrapper around connector loaders that handles database persistence.
    Uses the catalog's connector to load items from filesystem.
    """

    def __init__(self, catalog: Catalog, project: Project):
        self.catalog = catalog
        self.project = project

    def load_directory(self, path: str) -> List[CatalogItem]:
        """
        Load all items from directory using the catalog's connector.

        Returns a list of items in dependency order (parents before children).
        """
        catalog_path = Path(path)

        # Collect all YAML files in the catalog directory
        files: Dict[str, str] = {}
        for yaml_file in catalog_path.rglob("*.yml"):
            relative_path = yaml_file.relative_to(catalog_path)
            # Normalize to forward slashes
            normalized_path = str(relative_path).replace("\\", "/")
            with open(yaml_file, "r") as f:
                files[normalized_path] = f.read()

        # Use connector's loader to parse files into items
        connector = self.catalog.get_connector()
        loader = connector.make_loader()
        items = loader.load_from_files(files)

        return items

    def reload_file(self, file_path: Path) -> Optional[List[CatalogItem]]:
        """
        Load a single file using the connector's loader.

        Returns items from that specific file only.
        """
        # Check if file exists
        if not file_path.exists():
            return None

        catalog_path = Path(self.catalog.path)
        relative_path = file_path.relative_to(catalog_path)
        normalized_path = str(relative_path).replace("\\", "/")

        # Build files dict - include the target file and any context files needed
        files: Dict[str, str] = {}

        # Always include database.yml if it exists (provides context for table files)
        database_yml = catalog_path / "database.yml"
        if database_yml.exists():
            with open(database_yml, "r") as f:
                files["database.yml"] = f.read()

        # Read the target file
        with open(file_path, "r") as f:
            files[normalized_path] = f.read()

        # Use connector's loader with files
        connector = self.catalog.get_connector()
        loader = connector.make_loader()
        all_items = loader.load_from_files(files)

        # Filter to only items from the target file
        items = [item for item in all_items if item.file_path == normalized_path]

        return items if items else None

    def get_relative_file_path(self, file_path: Path) -> str:
        """Get file path relative to catalog root."""
        catalog_path = Path(self.catalog.path)
        return str(file_path.relative_to(catalog_path))

    def commit_items(self, items: List[CatalogItem]):
        """
        Commit items to database with proper validation and dependency resolution.

        - Generate all IDs when required
        - Check for any invalid entries and log warnings:
            - missing parents
        - If parent is set, set that as parent ID otherwise skip resource and log warning
        - Commit to DB
        """
        # Create a registry to track committed items by their key
        committed_items: Dict[str, str] = {}  # key -> item_id

        for catalog_item in items:
            # Generate deterministic ID
            item_id = self.catalog.gen_id(catalog_item.key)

            # Resolve parent ID if parent_key is set
            parent_id = None
            if catalog_item.parent_key:
                if catalog_item.parent_key in committed_items:
                    parent_id = committed_items[catalog_item.parent_key]
                else:
                    # Try to generate parent ID directly (parent might be committed in previous runs)
                    parent_parts = catalog_item.parent_key.split(".")
                    if len(parent_parts) == 1:
                        pass
                    elif len(parent_parts) == 2:
                        pass
                    elif len(parent_parts) == 3:
                        pass
                    else:
                        pass

                    parent_id = self.catalog.gen_id(catalog_item.parent_key)

            # Create Item object
            item = Item(
                id=item_id,
                catalog_id=self.catalog.id,
                name=catalog_item.name,
                key=catalog_item.key,
                type=catalog_item.type,
                sub_type=catalog_item.sub_type,
                data_type=catalog_item.data_type,
                parent_id=parent_id,
                description=catalog_item.description,
                notes=catalog_item.notes,
                properties=catalog_item.properties,
                archived=catalog_item.archived,
                file_path=catalog_item.file_path,
            )

            # Insert item into database
            insert_item(self.project, item)

            # Track committed item
            committed_items[catalog_item.key] = item_id


def reload_file(project: Project, catalog: Catalog, path: str):
    """
    Reload a single file by:
    - create a loader
    - get items (not none if successful)
    - delete all existing db catalog items for this file path
    - commit new items back into db.
    """
    from datadict_cli.lib.queries import delete_items_by_file_path

    # Create loader
    loader = CatalogLoader(catalog, project)

    # Convert path to Path object
    file_path = Path(path)

    # Load items from the single file
    items = loader.reload_file(file_path)

    # If items were successfully loaded
    if items is not None:
        # Get relative file path for database operations
        relative_file_path = loader.get_relative_file_path(file_path)

        # Delete existing items with this file path
        delete_items_by_file_path(project, catalog.id, relative_file_path)

        # Commit new items to database
        loader.commit_items(items)


def load_catalog(project: Project, catalog_name: str, catalog_path: str) -> Catalog:
    """
    Load a catalog from the given path
    - determine the catalog type
    - call appropriate builder for this project type like db_catalog etc
    """
    catalog_file = Path(catalog_path) / "catalog.yml"

    if not catalog_file.exists():
        raise FileNotFoundError(f"Catalog file not found: {catalog_file}")

    # Load and validate catalog YAML
    yaml = YAML(typ="safe")
    with open(catalog_file, "r") as f:
        catalog_data = yaml.load(f)

    # Type checker can't verify YAML content, but we validate with Pydantic
    catalog_config = CatalogConfig(**catalog_data)  # type: ignore

    # Create catalog instance with deterministic ID
    catalog_type = catalog_config.type or CatalogType.DATABASE
    catalog_id = generate_deterministic_id(catalog_config.name)

    catalog = Catalog(id=catalog_id, name=catalog_config.name, type=catalog_type, path=catalog_path)
    catalog.set_project(project)

    # Insert catalog into database
    insert_catalog(project, catalog)

    # Create loader and load items
    loader = CatalogLoader(catalog, project)
    items = loader.load_directory(catalog_path)
    loader.commit_items(items)

    return catalog
