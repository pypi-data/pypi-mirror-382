"""Utilities for resolving lineage relationships from raw edges."""

from __future__ import annotations

from typing import Iterable, Optional, Set, Tuple

import pandas as pd
from datadict_cli.lib.models import Lineage, Project, RawLineageEdge
from datadict_cli.lib.queries import (
    clear_lineage,
    fetch_raw_lineage,
    find_items_by_key,
    insert_lineages,
)


def build_lineage(project: Project, edges: Iterable[RawLineageEdge]) -> list[Lineage]:
    """Resolve raw lineage edges into item-to-item lineage relationships."""
    resolved: list[Lineage] = []
    seen: Set[Tuple[str, str, str]] = set()

    for edge in edges:
        exact_match = bool(edge.properties.get("exact_match", True))
        upstream_items = find_items_by_key(project, edge.src_key, exact_match=exact_match)
        downstream_items = find_items_by_key(project, edge.dst_key, exact_match=exact_match)

        for upstream in upstream_items:
            for downstream in downstream_items:
                dedupe_key = (upstream.id, downstream.id, edge.edge_type)
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)

                resolved.append(
                    Lineage(
                        upstream_catalog_id=upstream.catalog_id,
                        upstream_item_id=upstream.id,
                        upstream_key=upstream.key or edge.src_key,
                        downstream_catalog_id=downstream.catalog_id,
                        downstream_item_id=downstream.id,
                        downstream_key=downstream.key or edge.dst_key,
                        edge_type=edge.edge_type,
                        properties=edge.properties.copy(),
                    )
                )

    return resolved


def sync_project_lineage(project: Project, catalog_id: Optional[str] = None) -> list[Lineage]:
    """Rebuild resolved lineage edges from persisted raw edges."""
    raw_edges = fetch_raw_lineage(project, catalog_id)

    # Clear existing lineage state for the target scope before rebuilding
    clear_lineage(project, catalog_id)

    if not raw_edges:
        return []

    lineages = build_lineage(project, raw_edges)
    insert_lineages(project, lineages)
    return lineages


def dataframe_to_raw_edges(df: Optional[pd.DataFrame], catalog_id: str) -> list[RawLineageEdge]:
    """Convert a DataFrame of raw edges into model instances."""
    if df is None or df.empty:
        return []

    edges: list[RawLineageEdge] = []
    for _, row in df.iterrows():
        src_key = row.get("src_key")
        dst_key = row.get("dst_key")
        if not src_key or not dst_key:
            continue

        edge_type = row.get("edge_type") or "depends_on"
        properties = row.get("properties") or {}
        if not isinstance(properties, dict):
            properties = {}

        edges.append(
            RawLineageEdge(
                src_key=str(src_key),
                dst_key=str(dst_key),
                edge_type=str(edge_type),
                properties=properties,
                source_catalog_id=catalog_id,
            )
        )

    return edges
