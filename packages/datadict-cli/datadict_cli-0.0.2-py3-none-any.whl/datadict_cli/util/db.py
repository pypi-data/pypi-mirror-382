import sqlite3
from pathlib import Path
from typing import Optional

DEFAULT_DIRNAME = ".datadict"
DEFAULT_SUBDIR = "db"
DEFAULT_FILENAME = "datadict.db"


def default_project_db_path(project_path: str) -> str:
    """Compute the default on-disk path for the project database."""
    base = Path(project_path)
    return str(base / DEFAULT_DIRNAME / DEFAULT_SUBDIR / DEFAULT_FILENAME)


class DB:
    """
    Wrapper for a sqlite database
    Contains simple methods like running query, etc. does not know about the structure
    """

    def __init__(self, db_path: str = ":memory:"):
        self.path = db_path
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self):
        """Initialize the database tables"""
        self.execute("""
            CREATE TABLE IF NOT EXISTS catalogs (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT DEFAULT 'database',
                path TEXT NOT NULL,
                config TEXT
            )
        """)

        self.execute("""
            -- items table stores the generic item hierarchy for all catalogs.
            -- key is a nullable logical fully-qualified name representing the remote path
            -- (e.g., database.schema.table or dataset.view). It maps the remote hierarchy
            -- to local files and can be absent when not applicable.
            CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY,
                catalog_id TEXT NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                sub_type TEXT,
                data_type TEXT,
                parent_id TEXT,
                description TEXT,
                notes TEXT,
                properties TEXT,
                archived BOOLEAN DEFAULT FALSE,
                key TEXT,
                file_path TEXT,
                FOREIGN KEY (catalog_id) REFERENCES catalogs (id),
                FOREIGN KEY (parent_id) REFERENCES items (id)
            )
        """)

        # Project metadata table tracks high-level project info for DB-only loads
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS project_metadata (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                name TEXT NOT NULL,
                version TEXT NOT NULL
            )
            """
        )

        # Create indexes for performance
        self.execute("CREATE INDEX IF NOT EXISTS idx_items_catalog_id ON items(catalog_id)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_items_parent_id ON items(parent_id)")

        # Raw objects: nodes in an external graph (tables, views, jobs, etc.)
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS raw_objects (
                key TEXT PRIMARY KEY,
                type TEXT,
                name TEXT,
                sub_type TEXT,
                properties TEXT,
                origin TEXT,
                last_seen_at TIMESTAMP
            )
            """
        )

        # Raw lineage edges between objects
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS raw_lineage (
                src_key TEXT NOT NULL,
                dst_key TEXT NOT NULL,
                edge_type TEXT NOT NULL,
                properties TEXT,
                source_catalog_id TEXT,
                PRIMARY KEY (src_key, dst_key, edge_type)
            )
            """
        )

        # Ensure legacy databases have source_catalog_id column
        columns = [row["name"] for row in self.fetchall("PRAGMA table_info(raw_lineage)")]
        if "source_catalog_id" not in columns:
            self.execute("ALTER TABLE raw_lineage ADD COLUMN source_catalog_id TEXT")

        # Raw DDL or creation SQL per object
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS raw_ddl (
                key TEXT PRIMARY KEY,
                dialect TEXT,
                create_sql TEXT,
                collected_at TIMESTAMP
            )
            """
        )

        # Helpful indexes for raw metadata
        self.execute("CREATE INDEX IF NOT EXISTS idx_lineage_src ON raw_lineage(src_key)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_lineage_dst ON raw_lineage(dst_key)")
        self.execute(
            "CREATE INDEX IF NOT EXISTS idx_lineage_source_catalog ON raw_lineage(source_catalog_id)"
        )

        # Resolved lineage edges between items
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS lineage (
                upstream_catalog_id TEXT NOT NULL,
                upstream_item_id TEXT NOT NULL,
                upstream_key TEXT NOT NULL,
                downstream_catalog_id TEXT NOT NULL,
                downstream_item_id TEXT NOT NULL,
                downstream_key TEXT NOT NULL,
                edge_type TEXT NOT NULL DEFAULT 'depends_on',
                properties TEXT,
                PRIMARY KEY (upstream_item_id, downstream_item_id)
            )
            """
        )
        self.execute(
            "CREATE INDEX IF NOT EXISTS idx_resolved_lineage_upstream ON lineage(upstream_item_id)"
        )
        self.execute(
            "CREATE INDEX IF NOT EXISTS idx_resolved_lineage_downstream ON lineage(downstream_item_id)"
        )

        self.commit()

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query and return the cursor"""
        return self.connection.execute(query, params)

    def fetchone(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Execute a query and return one row"""
        cursor = self.execute(query, params)
        return cursor.fetchone()

    def fetchall(self, query: str, params: tuple = ()) -> list[sqlite3.Row]:
        """Execute a query and return all rows"""
        cursor = self.execute(query, params)
        return cursor.fetchall()

    def commit(self):
        """Commit the transaction"""
        self.connection.commit()

    def close(self):
        """Close the database connection"""
        self.connection.close()

    def reset_model_state(self):
        """Clear catalog/item state while keeping persistent raw metadata."""
        self.execute("DELETE FROM items")
        self.execute("DELETE FROM catalogs")
        self.execute("DELETE FROM project_metadata")
        self.commit()

    def upsert_project_metadata(self, *, name: str, version: str) -> None:
        """Persist project metadata for DB-only project loading."""
        self.execute(
            """
            INSERT INTO project_metadata (id, name, version)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                version = excluded.version
            """,
            (name, version),
        )
        self.commit()
