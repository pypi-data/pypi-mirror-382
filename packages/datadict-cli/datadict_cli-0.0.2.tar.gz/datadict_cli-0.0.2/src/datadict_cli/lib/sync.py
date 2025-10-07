"""
Metadata synchronization module for DataDict.

This module handles synchronization between remote metadata sources (databases, APIs, etc.)
and local DataDict catalogs. It compares metadata states and generates ordered change operations
to bring local data in sync with remote sources.

Key Design Principles:
- Source-agnostic: Works with any remote metadata source
- Side-effect free: Functions only compute changes, don't apply them
- Hierarchical-aware: Handles parent-child relationships correctly
- Filesystem-independent: Change application is handled elsewhere

Data Format:
Both remote and local data are provided as pandas DataFrames with these columns:
- type: Item type (database, schema, table, column)
- name: Item name
- key: Fully qualified name (e.g., "database.schema.table")
- sub_type: Optional subtype classification
- data_type: Data type information (for columns)
- parent_key: Parent's fully qualified name (null for root items)

Local data includes an additional column:
- archived: Boolean flag indicating if item is archived

Change Ordering Rules:
1. Changes are returned in four separate arrays: create, modify, archive, unarchive
2. Each array is ordered by tree depth (root items first, then children)
3. Reparenting operations require archiving all children of the moved subtree
4. Archived items missing from remote are ignored (no change needed)

Special Cases:
- Reparenting: When parent_key changes, archive entire subtree and recreate under new parent
- Archived items: Items archived locally but missing from remote are left unchanged
"""

import hashlib

import pandas as pd

from .types import ChangeType, ItemChange, SyncChanges


def calculate_metadata_checksum(row: pd.Series, exclude_columns: set[str] | None = None) -> str:
    """
    Calculate checksum for metadata row, excluding specified columns.

    Args:
        row: pandas Series representing a single item's metadata
        exclude_columns: Set of column names to exclude from checksum (default: {'archived'})

    Returns:
        Hex string checksum of the row's metadata
    """
    if exclude_columns is None:
        # Exclude operational/derived columns that shouldn't affect value comparisons
        exclude_columns = {
            "archived",
            "id",
            "parent_id",
            "parent_key",
            "depth",
            "checksum",
            "_merge",
        }

    # Get all columns except excluded ones, sorted for consistency
    metadata_columns = sorted([col for col in row.index if col not in exclude_columns])

    # Create string representation of metadata values
    metadata_values = []
    for col in metadata_columns:
        value = row[col]
        # Handle None/NaN values consistently
        if pd.isna(value) or value is None:
            metadata_values.append("")
        else:
            metadata_values.append(str(value))

    # Join values with separator and create hash
    content = "|".join(metadata_values)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def add_checksum_column(df: pd.DataFrame, exclude_columns: set[str] | None = None) -> pd.DataFrame:
    """
    Add checksum column to DataFrame for metadata comparison.

    Args:
        df: DataFrame with item metadata
        exclude_columns: Set of column names to exclude from checksum (default: {'archived'})

    Returns:
        DataFrame with added 'checksum' column
    """
    if df.empty:
        return df.copy()

    df_copy = df.copy()
    df_copy["checksum"] = df_copy.apply(
        lambda row: calculate_metadata_checksum(row, exclude_columns), axis=1
    )
    return df_copy


def add_depth_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a 'depth' column which contains the index of the depth along with each column
    """
    if df.empty:
        return df.copy()

    result_df = df.copy()
    result_df["depth"] = -1

    # Normalize parent_key column
    if "parent_key" not in result_df.columns:
        result_df["parent_key"] = None
    if "key" not in result_df.columns:
        result_df["key"] = None

    # Roots: items with no parent_key
    root_mask = result_df["parent_key"].isna()
    result_df.loc[root_mask, "depth"] = 0

    # Map key -> depth for assigned nodes
    name_to_depth: dict[str, int] = {}
    for _, row in result_df[result_df["depth"] == 0].iterrows():
        fn = row.get("key")
        if isinstance(fn, str) and fn:
            name_to_depth[fn] = 0

    current_depth = 0
    while True:
        # Collect names at current depth
        names_at_current_depth = {k for k, v in name_to_depth.items() if v == current_depth}
        if not names_at_current_depth:
            break

        # Assign next level: parent_key in names_at_current_depth and depth not set
        next_level_mask = (result_df["depth"] == -1) & (
            result_df["parent_key"].isin(list(names_at_current_depth))
        )
        next_level = result_df[next_level_mask]
        if next_level.empty:
            break

        result_df.loc[next_level_mask, "depth"] = current_depth + 1
        for _, row in next_level.iterrows():
            fn = row.get("key")
            if isinstance(fn, str) and fn:
                name_to_depth[fn] = current_depth + 1

        current_depth += 1

    # Any remaining unassigned nodes (disconnected) get lowest priority depth
    result_df.loc[result_df["depth"] == -1, "depth"] = current_depth + 1

    return result_df


def extract_change_dataframes(remote_df: pd.DataFrame, local_df: pd.DataFrame) -> dict:
    """
    Extract different types of changes by merging remote and local dataframes.
    Returns a dictionary with modify, create, and archive dataframes.
    """
    remote_with_checksum = add_checksum_column(remote_df)
    local_with_checksum = add_checksum_column(local_df)

    merged = remote_with_checksum.merge(
        local_with_checksum,
        left_on="key",
        right_on="key",
        how="outer",
        indicator=True,
        suffixes=("_remote", "_local"),
    )

    create = merged[merged["_merge"] == "left_only"]
    archive = merged[merged["_merge"] == "right_only"]

    both_df = merged[merged["_merge"] == "both"]
    if both_df.empty:
        modify = both_df
    else:
        modify = both_df[both_df["checksum_remote"] != both_df["checksum_local"]]

    return {"modify": modify, "create": create, "archive": archive}


def _safe_get_value(row: pd.Series, key: str) -> str | None:
    """
    Safely extract value from pandas row, handling NaN values.

    Args:
        row: pandas Series
        key: column key to extract

    Returns:
        String value or None (never NaN)
    """
    value = row.get(key)
    if pd.isna(value) or value is None:
        return None
    return str(value) if not isinstance(value, str) else value


def get_changes(remote_df: pd.DataFrame, local_df: pd.DataFrame) -> SyncChanges:
    """
    Compare remote and local metadata DataFrames and generate ordered change operations.

    Args:
        remote_df: DataFrame with remote metadata (source of truth)
        local_df: DataFrame with local metadata (includes 'archived' column)

    Returns:
        SyncChanges object with four arrays of changes ordered by tree depth
    """
    # Normalize inputs (do not mutate args)
    remote = remote_df.copy()
    local = local_df.copy()

    # Ensure archived column exists on local for consistent logic
    if "archived" not in local.columns:
        local["archived"] = False

    # Ensure required columns exist for depth computation
    if "parent_key" not in remote.columns:
        remote["parent_key"] = None
    if "parent_key" not in local.columns:
        local["parent_key"] = None

    # Ensure key column exists
    if "key" not in remote.columns:
        remote["key"] = None
    if "key" not in local.columns:
        local["key"] = None

    # Compute per-tree depths to order operations correctly
    remote_with_depth = add_depth_column(remote)
    local_with_depth = add_depth_column(local)

    remote_depth_by_name: dict[str, int] = (
        {
            str(row["key"]): int(row["depth"])  # type: ignore[index]
            for _, row in remote_with_depth.iterrows()
            if isinstance(row.get("key"), str)
        }
        if not remote_with_depth.empty
        else {}
    )
    local_depth_by_name: dict[str, int] = (
        {
            str(row["key"]): int(row["depth"])  # type: ignore[index]
            for _, row in local_with_depth.iterrows()
            if isinstance(row.get("key"), str)
        }
        if not local_with_depth.empty
        else {}
    )

    # Merge to compute differences and access both sides' columns
    remote_wc = add_checksum_column(remote)
    local_wc = add_checksum_column(local)

    merged = remote_wc.merge(
        local_wc,
        on="key",
        how="outer",
        indicator=True,
        suffixes=("_remote", "_local"),
    )

    # Identify sets
    create_df = merged[merged["_merge"] == "left_only"]
    archive_df = merged[merged["_merge"] == "right_only"]

    both_df = merged[merged["_merge"] == "both"]
    # Prepare archived series as boolean for safe logical operations
    if "archived" in both_df.columns:
        archived_column = both_df["archived"].infer_objects(copy=False)
        archived_series = archived_column.fillna(False).astype(bool)
    else:
        archived_series = pd.Series(False, index=both_df.index)

    # Only consider modify for items not archived locally to avoid duplicate modify+unarchive
    if both_df.empty:
        modify_df = both_df
        unarchive_df = both_df
    else:
        checksum_diff = both_df["checksum_remote"] != both_df["checksum_local"]
        modify_df = both_df[checksum_diff & (~archived_series)]
        # Unarchive: present in both, archived locally
        unarchive_df = both_df[archived_series]

    # Build ItemChange lists
    create_changes: list[ItemChange] = []
    for _, row in create_df.iterrows():
        depth = remote_depth_by_name.get(_safe_get_value(row, "key"), 0)
        create_changes.append(
            ItemChange(
                change=ChangeType.CREATE,
                type=_safe_get_value(row, "type_remote"),
                name=_safe_get_value(row, "name_remote"),
                key=_safe_get_value(row, "key"),
                sub_type=_safe_get_value(row, "sub_type_remote"),
                data_type=_safe_get_value(row, "data_type_remote"),
                parent_key=_safe_get_value(row, "parent_key_remote"),
                depth=depth,
            )
        )

    modify_changes: list[ItemChange] = []
    for _, row in modify_df.iterrows():
        depth = remote_depth_by_name.get(_safe_get_value(row, "key"), 0)
        modify_changes.append(
            ItemChange(
                change=ChangeType.MODIFY,
                type=_safe_get_value(row, "type_remote"),
                name=_safe_get_value(row, "name_remote"),
                key=_safe_get_value(row, "key"),
                sub_type=_safe_get_value(row, "sub_type_remote"),
                data_type=_safe_get_value(row, "data_type_remote"),
                parent_key=_safe_get_value(row, "parent_key_remote"),
                depth=depth,
            )
        )

    archive_changes: list[ItemChange] = []
    for _, row in archive_df.iterrows():
        # Skip if already archived locally and missing remotely (no-op per rules)
        archived_val = row.get("archived", False)
        try:
            is_archived = False if pd.isna(archived_val) else bool(archived_val)
        except Exception:
            is_archived = False
        if is_archived:
            continue
        depth = local_depth_by_name.get(_safe_get_value(row, "key"), 0)
        archive_changes.append(
            ItemChange(
                change=ChangeType.ARCHIVE,
                type=_safe_get_value(row, "type_local"),
                name=_safe_get_value(row, "name_local"),
                key=_safe_get_value(row, "key"),
                sub_type=_safe_get_value(row, "sub_type_local"),
                data_type=_safe_get_value(row, "data_type_local"),
                parent_key=_safe_get_value(row, "parent_key_local"),
                depth=depth,
            )
        )

    unarchive_changes: list[ItemChange] = []
    for _, row in unarchive_df.iterrows():
        fn = _safe_get_value(row, "key")
        depth = remote_depth_by_name.get(fn, local_depth_by_name.get(fn, 0))
        unarchive_changes.append(
            ItemChange(
                change=ChangeType.UNARCHIVE,
                type=_safe_get_value(row, "type_remote"),
                name=_safe_get_value(row, "name_remote"),
                key=_safe_get_value(row, "key"),
                sub_type=_safe_get_value(row, "sub_type_remote"),
                data_type=_safe_get_value(row, "data_type_remote"),
                parent_key=_safe_get_value(row, "parent_key_remote"),
                depth=depth,
            )
        )

    # Order by depth (root first)
    create_changes.sort(key=lambda c: (c.depth or 0, c.key or ""))
    modify_changes.sort(key=lambda c: (c.depth or 0, c.key or ""))
    archive_changes.sort(key=lambda c: (c.depth or 0, c.key or ""))
    unarchive_changes.sort(key=lambda c: (c.depth or 0, c.key or ""))

    return SyncChanges(
        create=create_changes,
        modify=modify_changes,
        archive=archive_changes,
        unarchive=unarchive_changes,
    )
