"""
Pure function utilities to serialize catalog items
"""

from typing import List, Optional, Tuple

from datadict_cli.lib.models import Catalog, Item, Project
from datadict_cli.lib.queries import find_catalog_items, find_item, find_lineage_by_item
from datadict_cli.lib.serializer.api_schemas import (
    CatalogOut,
    ItemChildrenOut,
    ItemOut,
    ItemRef,
    LineageOut,
    ProjectOut,
    TocItem,
)
from datadict_cli.lib.types import ItemType
from pydantic import BaseModel


def should_serialize_item(item: Item) -> bool:
    """
    Determine if an item should be serialized as a standalone item

    Items like columns are not serialized standalone - they're only
    included in their parent's children list.
    """
    # TODO: Move logic to db_serializer
    if item.type == ItemType.COLUMN:
        return False

    return True


def item_to_basic_output(item: Item) -> ItemOut:
    """Convert an item to ItemOut without lineage metadata."""
    return ItemOut(
        id=item.id,
        type=item.type,
        name=item.name,
        description=item.description,
        notes=item.notes,
        properties=item.properties if item.properties else None,
        lineage=None,
    )


def item_to_output(item: Item) -> ItemOut:
    """
    Convert an Item model to ItemOut schema for core item data (no children)
    """
    lineage_data = None

    try:
        project = item.get_project()
        lineages = find_lineage_by_item(project, item.id, direction="both")

        if lineages:
            lineage_items: list[LineageOut] = []
            seen: set[tuple[str, str, str]] = set()

            for lineage in lineages:
                dedupe_key = (
                    lineage.upstream_item_id,
                    lineage.downstream_item_id,
                    lineage.edge_type,
                )
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)

                upstream_item = find_item(project, lineage.upstream_item_id, with_children=False)
                downstream_item = find_item(
                    project, lineage.downstream_item_id, with_children=False
                )

                if not upstream_item or not downstream_item:
                    continue

                lineage_items.append(
                    LineageOut(
                        upstream=ItemRef(
                            id=upstream_item.id,
                            name=upstream_item.name,
                            type=upstream_item.type,
                            key=upstream_item.key,
                            catalog_id=upstream_item.catalog_id,
                        ),
                        downstream=ItemRef(
                            id=downstream_item.id,
                            name=downstream_item.name,
                            type=downstream_item.type,
                            key=downstream_item.key,
                            catalog_id=downstream_item.catalog_id,
                        ),
                    )
                )

            if lineage_items:
                lineage_data = lineage_items
    except (ValueError, AttributeError):
        lineage_data = None

    return ItemOut(
        id=item.id,
        type=item.type,
        name=item.name,
        description=item.description,
        notes=item.notes,
        properties=item.properties if item.properties else None,
        lineage=lineage_data,
    )


def item_to_children_output(item: Item) -> ItemChildrenOut:
    """
    Convert an Item model to ItemChildrenOut schema for children data
    """
    child_items = []
    if item.children:
        child_items = [item_to_basic_output(child) for child in item.children]

    return ItemChildrenOut(
        id=item.id,
        children=child_items,
    )


def get_toc(catalog: Catalog, project: Project) -> List[TocItem]:
    """
    Get the table of contents for a catalog

    For database catalogs, this creates a sidebar hierarchy:
    - Databases
      - Schemas

    Tables are not included in TOC since they would clutter the sidebar.
    Users navigate to schemas, then see tables within that schema.
    """
    toc_items = []
    root_items = find_catalog_items(project, catalog.id)
    # TODO: Move logic to db_serializer

    for root_item in root_items:
        if root_item.type == "database":
            # Create database TOC item
            db_children = []
            for schema in root_item.children:
                if schema.type == "schema":
                    # Create schema TOC item (no children - tables not in sidebar)
                    schema_item = TocItem(
                        id=schema.id,
                        name=schema.name,
                        url=f"/schema/{schema.id}",  # Schema page will show its tables
                        children=[],
                    )
                    db_children.append(schema_item)

            db_item = TocItem(
                id=root_item.id,
                name=root_item.name,
                url=f"/database/{root_item.id}",  # Database page will show its schemas
                children=db_children,
            )
            toc_items.append(db_item)

    return toc_items


def get_all_items_recursive(project: Project, item_id: str) -> List[Item]:
    """
    Get all items recursively starting from a given item
    """
    items = []
    item = find_item(project, item_id, with_children=True)
    if item:
        items.append(item)
        for child in item.children:
            items.extend(get_all_items_recursive(project, child.id))
    return items


def serialize_item(item: Item) -> Optional[Tuple[str, ItemOut]]:
    """
    Serialize core item data

    Returns (file_path, model) tuple for the item data
    """
    if not should_serialize_item(item):
        # Don't serialize items like columns that are part of parent
        return None

    item_out = item_to_output(item)
    file_path = f"item/{item.id}.json"

    return (file_path, item_out)


def serialize_children(item: Item) -> Optional[Tuple[str, ItemChildrenOut]]:
    """
    Serialize item children references

    Returns (file_path, model) tuple for the children data
    """
    if not should_serialize_item(item):
        # Don't serialize items like columns that are part of parent
        return None

    children_out = item_to_children_output(item)
    file_path = f"children/{item.id}.json"

    return (file_path, children_out)


def serialize_catalog(catalog: Catalog, project: Project) -> Tuple[str, CatalogOut]:
    """
    Serialize a catalog with table of contents
    """
    toc = get_toc(catalog, project)

    catalog_out = CatalogOut(
        id=catalog.id,
        name=catalog.name,
        type=catalog.type,
        path=catalog.path,
        toc=toc,
    )

    file_path = f"catalog/{catalog.id}.json"

    return (file_path, catalog_out)


def serialize_project(project: Project) -> Tuple[str, ProjectOut]:
    """
    Serialize project overview
    """
    project_out = ProjectOut(
        name=project.project_name,
        version=project.version,
        catalogs=[catalog.id for catalog in project.catalogs],
    )

    file_path = "project.json"

    return (file_path, project_out)


def get_build_tree(project: Project) -> List[Tuple[str, BaseModel]]:
    """
    Generate a complete build tree for a project

    Returns list of (file_path, model) tuples with structured data
    """
    build_files = []

    # Serialize project overview
    project_file = serialize_project(project)
    build_files.append(project_file)

    # Serialize each catalog and its items
    for catalog in project.catalogs:
        # Serialize catalog with TOC
        catalog_file = serialize_catalog(catalog, project)
        build_files.append(catalog_file)

        # Serialize all items in catalog
        root_items = find_catalog_items(project, catalog.id)
        for root_item in root_items:
            all_items = get_all_items_recursive(project, root_item.id)
            for item in all_items:
                # Serialize core item data
                item_file = serialize_item(item)
                if item_file:  # Some items like columns might return None
                    build_files.append(item_file)

                # Serialize children data
                children_file = serialize_children(item)
                if children_file:  # Some items like columns might return None
                    build_files.append(children_file)

    return build_files
