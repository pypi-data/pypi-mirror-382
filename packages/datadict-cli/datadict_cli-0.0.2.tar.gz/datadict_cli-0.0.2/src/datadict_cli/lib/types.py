from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ItemType(str, Enum):
    """
    Enum for item types that control frontend rendering and business logic.

    These types determine how items are displayed and processed in the frontend.
    """

    DATABASE = "database"
    SCHEMA = "schema"
    TABLE = "table"
    COLUMN = "column"
    DOC = "doc"  # Documentation
    TEST = "test"
    LOGIC = "logic"  # transformation like macros/analyses etc
    CONFIG = "config"  # Configuration rules


class CatalogType(str, Enum):
    """
    Enum for catalog types.

    Catalogs represent different data sources that can be loaded into DataDict.
    """

    DATABASE = "database"
    DBT = "dbt"
    # Future catalog types can be added here:
    # LOOKER = "looker"
    # TABLEAU = "tableau"


class ChangeType(str, Enum):
    """
    Enum for sync change operations.

    These represent the different types of changes that can be applied
    when syncing remote metadata with local data.
    """

    CREATE = "create"
    MODIFY = "modify"
    ARCHIVE = "archive"
    UNARCHIVE = "unarchive"


class WalkTreeResultType(str, Enum):
    """
    Enum for nodes in a physical path walk tree for database catalogs.
    """

    DATABASE = "database"
    SCHEMA = "schema"
    TABLE = "table"


class ItemChange(BaseModel):
    """
    Represents a single change operation to synchronize local metadata with remote.

    Fields are optional except for change type. The `id` may be omitted by
    upstream sync logic; when absent, downstream appliers (e.g., db_apply_change)
    should generate a deterministic ID based on `key`.
    """

    id: Optional[str] = None
    change: ChangeType

    # Core item metadata (optional to support partial updates)
    type: Optional[str] = None
    name: Optional[str] = None
    key: Optional[str] = None
    sub_type: Optional[str] = None
    data_type: Optional[str] = None
    # Prefer parent_key for dedup and hierarchy handling in sync
    parent_key: Optional[str] = None
    # Deprecated in sync: retained for compatibility with loaders/DB
    parent_id: Optional[str] = None

    # Computed field for change ordering (set during change calculation)
    depth: Optional[int] = None


class SyncChanges(BaseModel):
    """
    Structured result of synchronization change detection.

    Contains four arrays of changes ordered by tree depth to ensure proper
    dependency handling during application.
    """

    create: list[ItemChange] = []
    modify: list[ItemChange] = []
    archive: list[ItemChange] = []
    unarchive: list[ItemChange] = []
