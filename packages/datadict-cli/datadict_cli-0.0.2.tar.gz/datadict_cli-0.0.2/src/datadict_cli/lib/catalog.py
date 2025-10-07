import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from datadict_cli.lib.lineage import dataframe_to_raw_edges
from datadict_cli.lib.models import Catalog, Project
from datadict_cli.lib.queries import replace_raw_lineage
from datadict_cli.lib.schemas import CatalogConfig
from datadict_cli.lib.sync import get_changes
from ruamel.yaml import YAML

logger = logging.getLogger(__name__)


@dataclass
class ReconcileResult:
    total_changes: int
    success_count: int
    error_count: int


def reconcile_catalog(catalog: Catalog, target: str | None = None) -> ReconcileResult:
    """
    Reconcile a catalog with its remote data source by synchronizing metadata changes.

    This function orchestrates the complete sync workflow:
    1. Extracts current local state from the project database
    2. Loads connection credentials using the catalog's profile configuration
    3. Connects to remote data source and pulls current metadata
    4. Calculates required changes (create, modify, archive, unarchive)
    5. Applies changes to filesystem in hierarchical order

    The function acts as a high-level orchestrator, delegating to well-tested components
    for each step. It provides user-friendly logging suitable for CLI usage.

    Args:
        catalog: Catalog object containing configuration, file paths, and project reference
        target: Optional target name for credential lookup (uses profile default if None)

    Raises:
        ValueError: If catalog profile is not configured or credentials not found
        ConnectionError: If unable to connect to remote data source
        Exception: For other sync or filesystem errors (logged and re-raised)

    Example:
        ```python
        project = load_project("/path/to/project")
        catalog = project.catalogs[0]  # First catalog
        reconcile_catalog(catalog, target="prod")
        ```

    Note:
        This function assumes the project database is already loaded with current
        catalog items. Run load_project() first to ensure proper initialization.
    """
    logger.info(f"Starting reconciliation for catalog '{catalog.name}'")

    project = catalog.get_project()

    try:
        # Step 1: Extract local state from project database
        logger.info("Extracting current local metadata state...")
        local_df = _get_local_state_dataframe(project, catalog)
        logger.info(f"Found {len(local_df)} local items")

        # Step 2: Load credentials using catalog profile
        logger.info("Loading connection credentials...")
        profile_name = _get_catalog_profile_name(catalog)
        if not profile_name:
            raise ValueError(f"Catalog '{catalog.name}' has no profile configured")

        credentials = _get_credentials(project, profile_name, target)
        if not credentials:
            target_info = f" (target: {target})" if target else ""
            raise ValueError(f"No credentials found for profile '{profile_name}'{target_info}")

        logger.info(f"Loaded credentials for profile '{profile_name}'")

        # Step 3: Get remote metadata using connector's source
        logger.info("Connecting to remote data source...")

        connector = catalog.get_connector()
        metadata_source = connector.make_source()
        logger.info("Using connector's metadata source")

        try:
            logger.info("Pulling remote metadata...")
            prepared_credentials = dict(credentials)
            if project.path:
                prepared_credentials.setdefault("__project_root", str(project.path))
            if catalog.path:
                prepared_credentials.setdefault("__catalog_root", str(catalog.path))
            metadata_source.set_credentials(prepared_credentials)
            remote_df = metadata_source.read_metadata()
            logger.info(f"Retrieved {len(remote_df)} remote items")

            lineage_df = metadata_source.read_lineage()
            if lineage_df is not None:
                raw_edges = dataframe_to_raw_edges(lineage_df, catalog.id)
                replace_raw_lineage(project, catalog, raw_edges)
                logger.info(
                    "Stored %s raw lineage edges",
                    len(raw_edges),
                )
        finally:
            metadata_source.close()

        # Step 4: Calculate sync changes
        logger.info("Calculating required changes...")
        sync_changes = get_changes(remote_df, local_df)

        total_changes = (
            len(sync_changes.create)
            + len(sync_changes.modify)
            + len(sync_changes.archive)
            + len(sync_changes.unarchive)
        )
        if total_changes == 0:
            logger.info("No changes required - catalog is already in sync")
            return ReconcileResult(total_changes=0, success_count=0, error_count=0)

        logger.info(
            f"Found {total_changes} changes: {len(sync_changes.create)} create, {len(sync_changes.modify)} modify, {len(sync_changes.archive)} archive, {len(sync_changes.unarchive)} unarchive"
        )

        # Step 5: Apply changes to filesystem
        logger.info("Applying changes to filesystem...")

        success_count = 0
        error_count = 0

        # Build lookup table mapping keys to file paths
        lookup_table = _build_lookup_table(project, catalog)

        # Get the appropriate applier from the catalog's connector
        connector = catalog.get_connector()
        applier = connector.make_applier()

        # Build a cache of file contents for appliers that need to merge changes
        file_cache: dict[str, str] = {}

        def get_file_content(path: str) -> str:
            """Get cached file content or empty string if file doesn't exist."""
            if path not in file_cache:
                file_path = Path(catalog.path) / path
                if file_path.exists():
                    with open(file_path, "r") as f:
                        file_cache[path] = f.read()
                else:
                    file_cache[path] = ""
            return file_cache[path]

        # Apply all changes in order (sync engine already orders them correctly)
        for change_list, change_type in [
            (sync_changes.create, "CREATE"),
            (sync_changes.modify, "MODIFY"),
            (sync_changes.archive, "ARCHIVE"),
            (sync_changes.unarchive, "UNARCHIVE"),
        ]:
            for change in change_list:
                try:
                    # Get physical change requests from applier
                    physical_requests = applier.apply_change(change, lookup_table)

                    # Execute each physical change request
                    for request in physical_requests:
                        file_path = Path(catalog.path) / request.path
                        file_path.parent.mkdir(parents=True, exist_ok=True)

                        if request.action == "set":
                            # Update file cache so subsequent changes see the new content
                            file_cache[request.path] = request.content
                            with open(file_path, "w") as f:
                                f.write(request.content)
                        elif request.action == "delete":
                            if file_path.exists():
                                file_path.unlink()
                            file_cache[request.path] = ""

                    if physical_requests:
                        success_count += 1
                        logger.debug(
                            f"{change_type}: {change.key} -> applied {len(physical_requests)} file changes"
                        )

                except Exception as e:
                    error_count += 1
                    logger.error(f"Error applying {change_type.lower()} for {change.key}: {e}")

        # Summary
        if error_count == 0:
            logger.info(f"Successfully applied all {success_count} changes")
        else:
            logger.warning(f"Applied {success_count} changes with {error_count} errors")

        logger.info(f"Reconciliation completed for catalog '{catalog.name}'")
        return ReconcileResult(
            total_changes=total_changes,
            success_count=success_count,
            error_count=error_count,
        )

    except Exception as e:
        logger.error(f"Reconciliation failed for catalog '{catalog.name}': {e}")
        raise


def _get_local_state_dataframe(project: Project, catalog: Catalog) -> pd.DataFrame:
    """
    Extract current local state from project database as pandas DataFrame.

    Converts SQLite database items to the standardized DataFrame format
    expected by the sync module, including the 'archived' column for local state.
    """
    # Get all items for this catalog from database
    if not project.db:
        raise ValueError("Project database is not initialized")

    all_items = project.db.fetchall(
        "SELECT * FROM items WHERE catalog_id = ?",
        (catalog.id,),
    )

    # Convert to DataFrame format expected by sync module
    rows = []
    # Build a quick lookup for parent key resolution
    id_to_key: dict[str, str] = {
        row["id"]: row["key"] for row in all_items if row["key"] is not None
    }

    for item in all_items:
        parent_key = id_to_key.get(item["parent_id"]) if item["parent_id"] else None
        rows.append(
            {
                "id": item["id"],
                "type": item["type"],
                "name": item["name"],
                "key": item["key"],
                "sub_type": item["sub_type"],
                "data_type": item["data_type"],
                "parent_id": item["parent_id"],
                "parent_key": parent_key,
                "archived": bool(item["archived"]),
            }
        )

    # Ensure DataFrame has correct columns even when empty
    if not rows:
        return pd.DataFrame(
            columns=[
                "id",
                "type",
                "name",
                "key",
                "sub_type",
                "data_type",
                "parent_id",
                "parent_key",
                "archived",
            ]
        )

    return pd.DataFrame(rows)


def _get_credentials(project: Project, profile_name: str, target: str | None = None) -> dict:
    """
    Load credentials from profiles.yml for the given profile and target.

    Args:
        project: Project object
        profile_name: Name of the profile to load
        target: Optional target name (uses default if None)

    Returns:
        Dictionary containing credentials
    """
    # Load profiles.yml from project path
    if not project.path:
        raise ValueError("Project path is required to load profiles")

    profiles_path = Path(project.path) / "profiles.yml"
    if not profiles_path.exists():
        raise FileNotFoundError(f"Profiles file not found: {profiles_path}")

    yaml = YAML(typ="safe")
    with open(profiles_path, "r") as f:
        profiles_data = yaml.load(f) or {}

    # Get the profile
    if profile_name not in profiles_data:
        raise ValueError(f"Profile '{profile_name}' not found in profiles.yml")

    profile = profiles_data[profile_name]

    # Get the target (use default if not specified)
    target_name = target or profile.get("target")
    if not target_name:
        raise ValueError(f"No target specified and profile '{profile_name}' has no default target")

    if "outputs" not in profile:
        raise ValueError(f"Profile '{profile_name}' has no outputs configured")

    if target_name not in profile["outputs"]:
        raise ValueError(f"Target '{target_name}' not found in profile '{profile_name}'")

    credentials = profile["outputs"][target_name]

    return credentials


def _build_lookup_table(project: Project, catalog: Catalog) -> dict[str, str]:
    """
    Build a lookup table mapping FQN keys to existing file paths.

    This is used by appliers to determine where to place new items or
    find existing items for modification.
    """
    if not project.db:
        return {}

    items = project.db.fetchall(
        "SELECT key, file_path FROM items WHERE catalog_id = ? AND key IS NOT NULL",
        (catalog.id,),
    )

    lookup_table = {}
    for item in items:
        if item["key"] and item["file_path"]:
            lookup_table[item["key"]] = item["file_path"]

    # Provide catalog root so appliers can resolve existing files for merges
    lookup_table["__catalog_root__"] = str(catalog.path)

    return lookup_table


def _get_catalog_profile_name(catalog: Catalog) -> str | None:
    """
    Extract profile name from catalog configuration.

    Loads the catalog.yml file and returns the profile name from the
    connection configuration, or None if not configured.
    """
    catalog_file = Path(catalog.path) / "catalog.yml"

    if not catalog_file.exists():
        return None

    # Load catalog YAML to get profile name
    yaml = YAML(typ="safe")
    with open(catalog_file, "r") as f:
        catalog_data = yaml.load(f)

    # Parse and validate with Pydantic
    catalog_config = CatalogConfig(**catalog_data)  # type: ignore

    if catalog_config.connection and catalog_config.connection.profile:
        return catalog_config.connection.profile

    return None
