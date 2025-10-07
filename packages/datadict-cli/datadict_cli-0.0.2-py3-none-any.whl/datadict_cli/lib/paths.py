"""
Path mapping utilities for converting logical resource names to safe filesystem paths.

This module provides robust path mapping functionality with collision handling,
Unicode normalization, and extensive customization options.

Note: Currently Unix-focused. Windows compatibility will be added in future versions.
TODO: Add Windows filesystem compatibility (reserved names, path length limits, etc.)
"""

import hashlib
import re
import unicodedata
from typing import Dict, List, Optional

from datadict_cli.lib.schemas import PathMapping


def build_path(
    parts: List[str], mapping: Optional[PathMapping] = None, extension: str = "yml"
) -> str:
    """
    Build a safe filesystem path from logical resource parts with collision handling.

    This function converts logical database resource names (database, schema, table, etc.)
    into safe filesystem paths, handling edge cases like long names, special characters,
    and collisions through deterministic hashing.

    Note: Currently Unix-focused. Windows compatibility will be added in future versions.

    Args:
        parts: List of path components [database, schema, table, etc.]
        mapping: Optional PathMapping config with customization options
        extension: File extension (default: "yml")

    Returns:
        Safe filesystem path with collision handling

    Examples:
        build_path(["mydb", "public", "users"])
        # -> "mydb/public/users.yml"

        build_path(["db", "schema", "very_long_table_name_that_exceeds_limits"])
        # -> "db/schema/very_long_table_name_that_exceeds_limi_a3f2.yml"

        build_path(["db", "schema", "用户表_🔥_special@chars"])
        # -> "db/schema/special_chars_b7d4.yml"
    """
    if not parts:
        return f"empty.{extension}"

    # Use default mapping if none provided
    if mapping is None:
        mapping = PathMapping()

    # Process each path component
    safe_parts = []
    for part in parts:
        safe_part = _normalize_path_component(part, mapping)
        safe_parts.append(safe_part)

    # Join parts and add extension
    if len(safe_parts) == 1:
        return f"{safe_parts[0]}.{extension}"
    else:
        # Last component gets the extension
        *dir_parts, filename = safe_parts
        return "/".join(dir_parts + [f"{filename}.{extension}"])


def _normalize_path_component(name: str, mapping: PathMapping) -> str:
    """
    Normalize a single path component to be filesystem-safe.

    Steps:
    1. Apply custom replacements
    2. Unicode normalization
    3. Character filtering
    4. Separator handling
    5. Case handling
    6. Handle empty result
    7. Reserved name handling
    8. Length truncation with collision handling
    """
    if not name:
        return "empty"

    # Step 1: Apply custom replacements
    normalized = name
    for replacement in mapping.replacements or []:
        normalized = normalized.replace(replacement.find, replacement.replace)

    # Step 2: Unicode normalization (decompose then remove accents)
    normalized = unicodedata.normalize("NFD", normalized)
    normalized = "".join(c for c in normalized if unicodedata.category(c) != "Mn")

    # Step 3: Character filtering - replace invalid chars
    safe_chars = []
    for char in normalized:
        if char in mapping.allowed_chars:
            safe_chars.append(char)
        else:
            safe_chars.append(mapping.replacement_char)

    result = "".join(safe_chars)

    # Step 4: Separator handling
    if mapping.collapse_separators:
        result = re.sub(f"{re.escape(mapping.replacement_char)}+", mapping.replacement_char, result)

    if mapping.trim_separators:
        result = result.strip(mapping.replacement_char)

    # Step 5: Case handling
    if not mapping.preserve_case:
        result = result.lower()

    # Step 6: Handle empty result (before reserved name check)
    if not result:
        result = "empty"

    # Step 7: Reserved name handling
    if result in mapping.reserved_names:
        result = f"{result}{mapping.reserved_suffix}"

    # Step 8: Length truncation with collision handling
    if len(result) > mapping.max_length:
        # Generate deterministic hash for collision resolution
        hash_input = f"{mapping.hash_seed}{name}"  # Use original name for hash
        hash_obj = hashlib.sha256(hash_input.encode("utf-8"))
        hash_suffix = hash_obj.hexdigest()[: mapping.hash_length]

        # Truncate to leave room for hash and separator
        available_length = mapping.max_length - mapping.hash_length - 1  # -1 for underscore
        if available_length < 1:
            # If hash is too long, just use hash
            result = hash_suffix
        else:
            truncated = result[:available_length]
            result = f"{truncated}_{hash_suffix}"

    return result


def _detect_collisions(
    parts_list: List[List[str]], mapping: Optional[PathMapping] = None
) -> Dict[str, List[str]]:
    """
    Detect potential path collisions for a batch of path parts.

    This is a utility function for analyzing collision patterns across
    multiple paths, useful for debugging and optimization.

    Args:
        parts_list: List of path part lists to check
        mapping: PathMapping configuration

    Returns:
        Dictionary mapping collision paths to original names that caused them
    """
    if mapping is None:
        mapping = PathMapping()

    path_to_originals: Dict[str, List[str]] = {}

    for parts in parts_list:
        if not parts:
            continue

        safe_path = build_path(parts, mapping, "yml")
        original_name = ".".join(parts)

        if safe_path not in path_to_originals:
            path_to_originals[safe_path] = []
        path_to_originals[safe_path].append(original_name)

    # Return only actual collisions
    return {path: originals for path, originals in path_to_originals.items() if len(originals) > 1}
