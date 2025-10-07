#
# This contains schemas for yaml files
# Pydantic has good yaml loading and validation
# Be permissive and not super strict

# IMPORTANT: do not use these classes outside of loading functions

from typing import Optional

from datadict_cli.lib.types import CatalogType
from pydantic import BaseModel, ConfigDict, Field


class PathReplacement(BaseModel):
    find: str
    replace: str


class PathMapping(BaseModel):
    """
    This config customizes how logical paths (database.schema.table) map to physical filesystem paths.

    Provides extensive customization for handling edge cases like long names, special characters,
    and collision resolution through deterministic hashing.

    Note: Currently Unix-focused. Windows compatibility will be added in future versions.
    """

    model_config = ConfigDict(extra="allow")

    # String replacement rules (applied first, in order)
    replacements: Optional[list[PathReplacement]] = []

    # Maximum length for file or directory name (before hash suffix)
    max_length: int = 64

    # Case handling
    preserve_case: bool = False

    # Hash configuration for collision resolution
    hash_length: int = 4  # Number of hash characters for disambiguation
    hash_seed: str = ""  # Optional seed for hash function (adds to hash input)

    # Character handling
    allowed_chars: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
    replacement_char: str = "_"  # Character to replace invalid chars with

    # Special handling
    collapse_separators: bool = True  # Collapse multiple separators into one
    trim_separators: bool = True  # Remove leading/trailing separators

    # Reserved names to avoid (Unix focus)
    reserved_names: list[str] = [
        ".",
        "..",
        "~",
        # Common problematic names
        "index",
        "main",
        "temp",
        "test",
        "config",
        "data",
    ]

    # Add suffix to reserved names
    reserved_suffix: str = "_file"


class ProjectConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    version: str
    config_version: Optional[int] = Field(None, alias="config-version")
    catalogs: list[str] = []


class CatalogConnection(BaseModel):
    model_config = ConfigDict(extra="allow")

    profile: Optional[str] = None


class CatalogConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    type: Optional[CatalogType] = CatalogType.DATABASE
    connection: Optional[CatalogConnection] = None


# Credential schemas for profiles.yml
class ProfileTarget(BaseModel):
    """
    Individual target within a profile (e.g., dev, prod, staging)
    """

    model_config = ConfigDict(extra="allow")

    type: str  # Database type (postgres, snowflake, etc.)
    # All other fields are arbitrary key-value pairs specific to the connection type


class Profile(BaseModel):
    """
    Profile configuration containing multiple targets
    """

    model_config = ConfigDict(extra="allow")

    target: Optional[str] = None  # Default target name
    outputs: dict[str, ProfileTarget] = {}  # Target name -> target config


class ProfilesConfig(BaseModel):
    """
    Complete profiles configuration (profiles.yml)
    """

    model_config = ConfigDict(extra="allow")

    # Profile name -> profile config
    # Using root validator to handle dynamic profile names
