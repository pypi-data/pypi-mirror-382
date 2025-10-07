# Queries for managing

import json
from typing import Optional

from datadict_cli.lib.models import Catalog, Item, Lineage, Project, RawLineageEdge


def _set_item_references(project: Project, item: Item):
    """Helper function to set weak references for an item."""
    item.set_project(project)

    # Find the catalog by catalog_id and set reference
    for catalog in project.catalogs:
        if catalog.id == item.catalog_id:
            item.set_catalog(catalog)
            break


def insert_catalog(project: Project, catalog: Catalog):
    """
    Insert catalog into database
    """
    if not project.db:
        raise ValueError("Project database not initialized")

    project.db.execute(
        """
        INSERT OR REPLACE INTO catalogs (id, name, type, path, config)
        VALUES (?, ?, ?, ?, ?)
    """,
        (catalog.id, catalog.name, catalog.type, catalog.path, json.dumps({})),
    )
    project.db.commit()


def insert_item(project: Project, item: Item):
    """
    Insert item into database and set weak references
    """
    if not project.db:
        raise ValueError("Project database not initialized")

    # Set weak references to project and catalog
    _set_item_references(project, item)

    project.db.execute(
        """
        INSERT OR REPLACE INTO items (id, catalog_id, name, type, sub_type, data_type, parent_id, description, notes, properties, archived, key, file_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            item.id,
            item.catalog_id,
            item.name,
            item.type,
            item.sub_type,
            item.data_type,
            item.parent_id,
            item.description,
            item.notes,
            json.dumps(item.properties),
            item.archived,
            item.key,
            item.file_path,
        ),
    )
    project.db.commit()


def find_item(project: Project, item_id: str, with_children: bool = True) -> Optional[Item]:
    """
    Find an item by ID, optionally with children
    """
    if not project.db:
        raise ValueError("Project database not initialized")

    row = project.db.fetchone("SELECT * FROM items WHERE id = ?", (item_id,))
    if not row:
        return None

    item = Item(
        id=row["id"],
        catalog_id=row["catalog_id"],
        name=row["name"],
        key=row["key"],
        type=row["type"],
        sub_type=row["sub_type"],
        data_type=row["data_type"],
        parent_id=row["parent_id"],
        description=row["description"],
        notes=row["notes"],
        properties=json.loads(row["properties"]) if row["properties"] else {},
        archived=bool(row["archived"]),
        file_path=row["file_path"],
    )

    # Set weak references to project and catalog
    _set_item_references(project, item)

    if with_children:
        children_rows = project.db.fetchall(
            "SELECT * FROM items WHERE parent_id = ? AND archived = FALSE ORDER BY name",
            (item_id,),
        )
        for child_row in children_rows:
            child_item = find_item(project, child_row["id"], with_children=True)
            if child_item:
                item.children.append(child_item)

    return item


def find_catalog_items(project: Project, catalog_id: str) -> list[Item]:
    """
    Find all root items in a catalog (items with no parent)
    """
    if not project.db:
        raise ValueError("Project database not initialized")

    rows = project.db.fetchall(
        """
        SELECT * FROM items
        WHERE catalog_id = ? AND parent_id IS NULL AND archived = FALSE
        ORDER BY name
    """,
        (catalog_id,),
    )

    items = []
    for row in rows:
        item = find_item(project, row["id"], with_children=True)
        if item:
            items.append(item)

    return items


def delete_items_by_file_path(project: Project, catalog_id: str, file_path: str):
    """
    Delete all items from a catalog that have a specific file_path.
    Used when reloading a single file to clear existing items before re-importing.
    """
    if not project.db:
        raise ValueError("Project database not initialized")

    project.db.execute(
        "DELETE FROM items WHERE catalog_id = ? AND file_path = ?",
        (catalog_id, file_path),
    )
    project.db.commit()


def find_items_by_key(project: Project, key: str, *, exact_match: bool = True) -> list[Item]:
    """Find active items by key with optional relaxed matching."""
    if not project.db:
        raise ValueError("Project database not initialized")

    if not key:
        return []

    keys_to_try = [key] if exact_match else _generate_key_variations(key)
    results: list[Item] = []

    for search_key in keys_to_try:
        rows = project.db.fetchall(
            """
            SELECT *
            FROM items
            WHERE key = ? AND archived = FALSE
            """,
            (search_key,),
        )

        for row in rows:
            item = Item(
                id=row["id"],
                catalog_id=row["catalog_id"],
                name=row["name"],
                key=row["key"],
                type=row["type"],
                sub_type=row["sub_type"],
                data_type=row["data_type"],
                parent_id=row["parent_id"],
                description=row["description"],
                notes=row["notes"],
                properties=json.loads(row["properties"]) if row["properties"] else {},
                archived=bool(row["archived"]),
                file_path=row["file_path"],
            )
            _set_item_references(project, item)
            results.append(item)

        if results:
            break

    return results


def _generate_key_variations(key: str) -> list[str]:
    """Relax matching by dropping leading segments from dotted keys."""
    parts = [segment for segment in key.split(".") if segment]
    if not parts:
        return []

    variations: list[str] = []
    for index in range(len(parts)):
        variations.append(".".join(parts[index:]))
    return variations


def insert_lineages(project: Project, lineages: list[Lineage]):
    """Bulk-upsert resolved lineage edges into the database."""
    if not project.db:
        raise ValueError("Project database not initialized")

    if not lineages:
        return

    values = [
        (
            lineage.upstream_catalog_id,
            lineage.upstream_item_id,
            lineage.upstream_key,
            lineage.downstream_catalog_id,
            lineage.downstream_item_id,
            lineage.downstream_key,
            lineage.edge_type,
            json.dumps(lineage.properties) if lineage.properties else None,
        )
        for lineage in lineages
    ]

    project.db.connection.executemany(
        """
        INSERT OR REPLACE INTO lineage (
            upstream_catalog_id,
            upstream_item_id,
            upstream_key,
            downstream_catalog_id,
            downstream_item_id,
            downstream_key,
            edge_type,
            properties
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        values,
    )
    project.db.commit()


def clear_lineage(project: Project, catalog_id: Optional[str] = None):
    """Clear resolved lineage edges, optionally scoped to a catalog."""
    if not project.db:
        raise ValueError("Project database not initialized")

    if catalog_id:
        project.db.execute(
            """
            DELETE FROM lineage
            WHERE upstream_catalog_id = ? OR downstream_catalog_id = ?
            """,
            (catalog_id, catalog_id),
        )
    else:
        project.db.execute("DELETE FROM lineage")

    project.db.commit()


def find_lineage_by_item(project: Project, item_id: str, direction: str = "both") -> list[Lineage]:
    """Return resolved lineage edges associated with an item."""
    if not project.db:
        raise ValueError("Project database not initialized")

    results: list[Lineage] = []

    if direction in ("upstream", "both"):
        rows = project.db.fetchall(
            """
            SELECT * FROM lineage WHERE downstream_item_id = ?
            """,
            (item_id,),
        )
        results.extend(_rows_to_lineages(rows))

    if direction in ("downstream", "both"):
        rows = project.db.fetchall(
            """
            SELECT * FROM lineage WHERE upstream_item_id = ?
            """,
            (item_id,),
        )
        results.extend(_rows_to_lineages(rows))

    return results


def find_all_lineage(project: Project) -> list[Lineage]:
    """Fetch all resolved lineage edges for the project."""
    if not project.db:
        raise ValueError("Project database not initialized")

    rows = project.db.fetchall("SELECT * FROM lineage")
    return _rows_to_lineages(rows)


def replace_raw_lineage(project: Project, catalog: Catalog, edges: list[RawLineageEdge]) -> None:
    """Replace raw lineage edges for a catalog with the provided list."""
    if not project.db:
        raise ValueError("Project database not initialized")

    project.db.execute(
        "DELETE FROM raw_lineage WHERE source_catalog_id = ?",
        (catalog.id,),
    )

    if edges:
        values = [
            (
                edge.src_key,
                edge.dst_key,
                edge.edge_type,
                json.dumps(edge.properties) if edge.properties else None,
                edge.source_catalog_id or catalog.id,
            )
            for edge in edges
        ]

        project.db.connection.executemany(
            """
            INSERT OR REPLACE INTO raw_lineage (
                src_key,
                dst_key,
                edge_type,
                properties,
                source_catalog_id
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            values,
        )

    project.db.commit()


def fetch_raw_lineage(project: Project, catalog_id: Optional[str] = None) -> list[RawLineageEdge]:
    """Fetch raw lineage edges, optionally filtering by catalog."""
    if not project.db:
        raise ValueError("Project database not initialized")

    if catalog_id:
        rows = project.db.fetchall(
            "SELECT * FROM raw_lineage WHERE source_catalog_id = ?",
            (catalog_id,),
        )
    else:
        rows = project.db.fetchall("SELECT * FROM raw_lineage")

    edges: list[RawLineageEdge] = []
    for row in rows:
        properties = json.loads(row["properties"]) if row["properties"] else {}
        source_catalog_id = None
        if "source_catalog_id" in row.keys():
            source_catalog_id = row["source_catalog_id"]
        edges.append(
            RawLineageEdge(
                src_key=row["src_key"],
                dst_key=row["dst_key"],
                edge_type=row["edge_type"],
                properties=properties,
                source_catalog_id=source_catalog_id,
            )
        )

    return edges


def _rows_to_lineages(rows) -> list[Lineage]:
    """Helper to convert sqlite rows to Lineage models."""
    lineages: list[Lineage] = []
    for row in rows:
        properties = json.loads(row["properties"]) if row["properties"] else {}
        lineages.append(
            Lineage(
                upstream_catalog_id=row["upstream_catalog_id"],
                upstream_item_id=row["upstream_item_id"],
                upstream_key=row["upstream_key"],
                downstream_catalog_id=row["downstream_catalog_id"],
                downstream_item_id=row["downstream_item_id"],
                downstream_key=row["downstream_key"],
                edge_type=row["edge_type"],
                properties=properties,
            )
        )
    return lineages
