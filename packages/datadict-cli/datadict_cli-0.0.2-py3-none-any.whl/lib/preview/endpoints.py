"""Compatibility forwarding for preview API endpoints."""

from datadict_cli.lib.preview.endpoints import *  # noqa: F401,F403

try:  # pragma: no cover
    from datadict_cli.lib.preview.endpoints import __all__ as __all__  # type: ignore[attr-defined]
except Exception:  # pragma: no cover
    __all__ = []  # type: ignore[assignment]
