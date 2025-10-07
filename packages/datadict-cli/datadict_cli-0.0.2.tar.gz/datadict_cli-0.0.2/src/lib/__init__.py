"""Compatibility layer exposing ``datadict_cli.lib`` under the legacy namespace."""

from datadict_cli.lib import *  # noqa: F401,F403

try:  # pragma: no cover - defensive fallback if __all__ not defined
    from datadict_cli.lib import __all__ as __all__  # type: ignore[attr-defined]
except Exception:  # pragma: no cover
    __all__ = []  # type: ignore[assignment]
