"""
Shared helpers for applying filesystem changes across catalog types.

This module centralizes common result types and small utilities used by
both the database and dbt catalog appliers. Keeping these here reduces
duplication and helps ensure consistent behavior across appliers.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from datadict_cli.lib.types import ChangeType, ItemChange
from pydantic import BaseModel
from ruamel.yaml import YAML


def new_yaml() -> YAML:
    """Return a YAML instance configured for our serialization needs."""
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096
    return yaml


class FileChangeType(str, Enum):
    """Types of file system changes that can result from applying an ItemChange."""

    CREATED = "created"  # New file was created
    MODIFIED = "modified"  # Existing file was updated
    NOOP = "noop"  # No changes needed (item already exists)
    ERROR = "error"  # Operation failed


class FileChange(BaseModel):
    """
    Result object returned by appliers containing details about filesystem changes.

    Tracks both the success/failure status and metadata about what files were affected.
    Useful for logging, dry-run modes, and rollback operations.
    """

    success: bool
    error_message: Optional[str] = None
    file_path: Optional[str] = None  # Primary file that was changed
    change_type: Optional[FileChangeType] = None
    file_contents: Optional[str] = None  # Contents of the changed file (for verification)
    created_dir: Optional[str] = None  # Directory created (for parent operations)
    created_file: Optional[str] = None  # New file created (for leaf operations)


@dataclass
class ChangeResult:
    """Result of applying a specific operation on a YAML document."""

    data: dict
    changed: bool
    created_dir: Optional[str] = None
    created_file: Optional[str] = None


class ChangeApplier:
    """
    Base class that encapsulates applying a change to a YAML-backed file.

    Subclasses implement domain-specific mutation logic while the base class
    handles locating the target file, reading/writing YAML, and reporting
    consistent FileChange results.
    """

    def __init__(self, catalog: Any, yaml: YAML | None = None) -> None:
        self.catalog = catalog
        self.yaml = yaml or new_yaml()

    # ---- Hooks to override ----
    def resolve_path(self, change: ItemChange) -> str:
        """Return relative path to target YAML file for this change."""
        raise NotImplementedError

    def requires_existing_file(self, change: ItemChange, op: ChangeType) -> bool:
        """
        Whether operation requires the YAML file to already exist.
        Defaults to True for non-create operations.
        """
        return op != ChangeType.CREATE

    def default_data_for_missing_file(self, change: ItemChange, op: ChangeType) -> dict:
        """Default initial data if the YAML file does not exist and creation is allowed."""
        return {}

    def create(self, change: ItemChange, data: dict, full_path: Path) -> ChangeResult:
        raise NotImplementedError

    def modify(self, change: ItemChange, data: dict, full_path: Path) -> ChangeResult:
        raise NotImplementedError

    def set_archived(
        self, change: ItemChange, data: dict, full_path: Path, archived: bool
    ) -> ChangeResult:
        raise NotImplementedError

    # ---- Orchestration ----
    def apply(self, change: ItemChange) -> FileChange:
        # Basic validation + id generation
        if not change.key:
            raise ValueError("ItemChange must have key")

        if not change.id:
            try:
                change.id = self.catalog.gen_id(change.key)
            except Exception:
                pass

        # Resolve target file
        self.catalog.get_project()
        relative_path = self.resolve_path(change)
        if not relative_path:
            raise ValueError(f"Could not resolve physical path for {change.key}")

        full_path = Path(self.catalog.path) / relative_path
        file_existed_before = full_path.exists()

        # Load YAML (or prepare defaults)
        if file_existed_before:
            with open(full_path, "r") as f:
                data = self.yaml.load(f) or {}
        else:
            if self.requires_existing_file(change, change.change):
                # Mirror the fail-fast behavior
                raise FileNotFoundError(str(full_path))
            data = self.default_data_for_missing_file(change, change.change)

        # Dispatch operation
        if change.change == ChangeType.CREATE:
            result = self.create(change, data, full_path)
        elif change.change == ChangeType.MODIFY:
            result = self.modify(change, data, full_path)
        elif change.change == ChangeType.ARCHIVE:
            result = self.set_archived(change, data, full_path, True)
        elif change.change == ChangeType.UNARCHIVE:
            result = self.set_archived(change, data, full_path, False)
        else:
            raise ValueError(f"Unsupported change type: {change.change}")

        if not result.changed:
            return FileChange(
                success=True,
                file_path=str(full_path),
                change_type=FileChangeType.NOOP,
            )

        # Ensure directory exists for writing
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write YAML
        with open(full_path, "w") as f:
            self.yaml.dump(result.data, f)

        with open(full_path, "r") as f:
            contents = f.read()

        change_type = FileChangeType.MODIFIED if file_existed_before else FileChangeType.CREATED

        return FileChange(
            success=True,
            file_path=str(full_path),
            change_type=change_type,
            file_contents=contents,
            created_dir=result.created_dir,
            created_file=result.created_file,
        )
