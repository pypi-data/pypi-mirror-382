"""Compatibility wrapper for ``datadict_cli.lib.preview``."""

from datadict_cli.lib.preview import *  # noqa: F401,F403

try:  # pragma: no cover - defensive fallback
    from datadict_cli.lib.preview import __all__ as __all__  # type: ignore[attr-defined]
except Exception:  # pragma: no cover
    __all__ = []  # type: ignore[assignment]
