import hashlib
import weakref
from typing import TYPE_CHECKING, Optional

from datadict_cli.lib.types import CatalogType, ItemType
from datadict_cli.util.db import DB
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    pass


def generate_deterministic_id(key: str) -> str:
    """
    Generate a deterministic UUID based on the key only.
    This ensures that the same logical item always gets the same ID.

    Note: This helper is deprecated and only retained for catalog id generation.
    Prefer calling `Catalog.gen_id(key)` everywhere else so catalog-specific
    entropy can be added in the future.
    """
    # Create a hash from the key
    hash_object = hashlib.sha256(key.encode("utf-8"))

    # Convert hash to UUID format
    hash_hex = hash_object.hexdigest()
    uuid_str = (
        f"{hash_hex[:8]}-{hash_hex[8:12]}-{hash_hex[12:16]}-{hash_hex[16:20]}-{hash_hex[20:32]}"
    )
    return uuid_str


class Item(BaseModel):
    """
    Core item model for all catalog entities.

    Design Constraint: All data fetched from remote databases must be stored
    in this unified schema to maintain consistency and enable generic operations.

    Field Definitions:
    - type: Controls frontend rendering and business logic (e.g., "table", "column")
    - subType: Native database type for more granular classification (e.g., "view", "materialized_view")
    - dataType: Column-specific data type (e.g., "varchar(255)", "integer")
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str
    catalog_id: str
    name: str
    # A logical fully qualified name representing the remote path (nullable)
    key: Optional[str] = None
    type: ItemType  # Frontend/business logic type (table, column, schema, etc.)
    sub_type: Optional[str] = None  # Native database type (view, materialized_view, etc.)
    data_type: Optional[str] = None  # Column data type (varchar, integer, etc.)
    parent_id: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    properties: dict = {}
    archived: bool = False
    file_path: Optional[str] = None  # Path to the YAML file where this item is stored
    children: list["Item"] = []

    # Weak references to parent objects
    _catalog_ref: Optional[weakref.ReferenceType] = None
    _project_ref: Optional[weakref.ReferenceType] = None

    def get_catalog(self) -> "Catalog":
        """Get the catalog this item belongs to."""
        if self._catalog_ref is None:
            raise ValueError(f"Item '{self.name}' has no catalog reference")
        catalog = self._catalog_ref()
        if catalog is None:
            raise ValueError(f"Item '{self.name}' catalog reference has been garbage collected")
        return catalog

    def set_catalog(self, catalog: "Catalog") -> None:
        """Set the catalog this item belongs to using a weak reference."""
        self._catalog_ref = weakref.ref(catalog)

    def get_project(self) -> "Project":
        """Get the project this item belongs to."""
        if self._project_ref is None:
            raise ValueError(f"Item '{self.name}' has no project reference")
        project = self._project_ref()
        if project is None:
            raise ValueError(f"Item '{self.name}' project reference has been garbage collected")
        return project

    def set_project(self, project: "Project") -> None:
        """Set the project this item belongs to using a weak reference."""
        self._project_ref = weakref.ref(project)


class Catalog(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str
    name: str
    type: CatalogType = CatalogType.DATABASE
    path: str
    _project_ref: Optional[weakref.ReferenceType] = None  # Weak reference to parent project

    # TODO: this is deprecated
    items: list[Item] = []

    def get_project(self) -> "Project":
        """Get the project this catalog belongs to."""
        if self._project_ref is None:
            raise ValueError(f"Catalog '{self.name}' has no project reference")
        project = self._project_ref()
        if project is None:
            raise ValueError(f"Catalog '{self.name}' project reference has been garbage collected")
        return project

    def set_project(self, project: "Project") -> None:
        """Set the project this catalog belongs to using a weak reference."""
        self._project_ref = weakref.ref(project)

    def gen_id(self, key: str) -> str:
        """
        Generate a deterministic ID for an object within this catalog.

        Currently identical to generate_deterministic_id(key), but exists
        as an instance method to allow catalog-specific entropy in the future.
        """
        return generate_deterministic_id(key)

    def get_connector(self):
        """
        Get the appropriate connector for this catalog type.

        TODO: This should be moved to a plugin system in phase 2 where connectors
        are discovered dynamically from installed packages rather than hardcoded.

        Returns:
            ConnectorBase instance (PostgresConnector or DbtConnector)
        """
        if self.type == CatalogType.DATABASE:
            from datadict_connector_postgres import PostgresConnector

            return PostgresConnector()
        elif self.type == CatalogType.DBT:
            from datadict_connector_dbt import DbtConnector

            return DbtConnector()
        else:
            raise ValueError(f"Unsupported catalog type: {self.type}")


class Project(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    project_name: str
    version: str
    path: Optional[str] = None  # Path to project root directory
    catalogs: list[Catalog] = []
    db: Optional[DB] = None


class RawLineageEdge(BaseModel):
    """Raw lineage relationship sourced from connectors using key references."""

    src_key: str
    dst_key: str
    edge_type: str = "depends_on"
    properties: dict = Field(default_factory=dict)
    source_catalog_id: Optional[str] = None


class Lineage(BaseModel):
    """Resolved lineage relationship between concrete catalog items."""

    upstream_catalog_id: str
    upstream_item_id: str
    upstream_key: str
    downstream_catalog_id: str
    downstream_item_id: str
    downstream_key: str
    edge_type: str = "depends_on"
    properties: dict = Field(default_factory=dict)
